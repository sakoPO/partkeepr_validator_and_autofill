import requests
from requests.auth import HTTPBasicAuth
import sys
import json
from decimal import Decimal
import time
from .part import Part
from .partkeepr_units import Units


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)


class Partkeepr:
    def __init__(self, config, debug=False, noEdit=False):
        self.config = config
        self.debug = debug
        self.noEdit = noEdit
        timestr = time.strftime("%Y_%m_%d-%H_%M_%S")
        self.log = open("partkeepr_" + timestr + ".log", 'w')

    def __del__(self):
        self.log.close()

    def get_part(self, part_id):
        params = {"itemsPerPage": 9999}
        response = self.api_call('get', '/api/parts/' + part_id, params=params)
        request = self.__convert_part_response_to_put_request(response.json())
        return Part(part_id, request, self.__get_units())

    def update_part(self, part):
        id = part.get_id()
        print("Updating part:", id)
        r = self.api_call('put', '/api/parts/' + id, json=part.request)
        r.raise_for_status()
        return r

    def edit_part_description(self, part_id, description):
        if part_id.startswith("/api/parts/"):
            part_id = part_id.replace("/api/parts/", "")
            response = self.get_component(part_id)
            old_description = response['description']
            self.log.write("Updating description of part: " + part_id + ", old description: " + old_description +
                           ", new description: " + description + "\n")
            request = self.__convert_part_response_to_put_request(response)
            request['description'] = description
            r = self.api_call('put', '/api/parts/' + part_id, json=request)
            r.raise_for_status()
            return r

    def edit_part_parameter(self, part_id, parameter_name, value):
        def update_value(parameter, value):
            si_prefix_map = {'value': 'siPrefix', 'maxValue': 'maxSiPrefix', 'minValue': 'minSiPrefix'}
            if parameter['valueType'] == 'numeric':
                for value_type in ['value', 'minValue', 'maxValue']:
                    if value[value_type] is not None:
                        prefix = parameter[si_prefix_map[value_type]]['symbol']
                        parameter[value_type] = float(value[value_type].get_value_as(prefix))
                    else:
                        parameter[value_type] = None
                        parameter[si_prefix_map[value_type]] = None
                return parameter

        if part_id.startswith("/api/parts/"):
            part_id = part_id.replace("/api/parts/", "")
            response = self.get_component(part_id)
            request = self.__convert_part_response_to_put_request(response)
            found = 0
            for parameter in request['parameters']:
                if parameter['name'] == parameter_name:
                    found += 1
                    old_parameter = parameter
            if found == 1:
                new_parameter = update_value(old_parameter, value)
                if old_parameter["valueType"] == "numeric":
                    self.log.write("Updating " + parameter_name + " parameter of part: " + part_id +
                                   ", old parameter: " + str(old_parameter) + ", new parameter: " + str(
                        new_parameter) + "\n")
                    r = self.api_call('put', '/api/parts/' + part_id, json=request)
                    r.raise_for_status()

    def find_part_parameter(self, name):
        r = self.api_call('get', '/api/parts/getPartParameterNames')
        found = []
        for parameter in r.json():
            if parameter["name"] == name:
                found.append(parameter)
        return found

    def get_component_request(self, part_id):
        if part_id.startswith("/api/parts/"):
            part_id = part_id.replace("/api/parts/", "")
            response = self.get_component(part_id)
            return self.__convert_part_response_to_put_request(response)

    def get_unit(self, name):
        units = self.__get_units()
        return units.get(name)

    def __get_units(self):
        params = {"itemsPerPage": 9999}
        r = self.api_call('get', '/api/units', params=params)
        rj = r.json()
        return Units(rj['hydra:member'])

    def api_call(self, method, url, **kwargs):
        """calls Partkeepr API

        :method: requst method
        :url: part of the url to call (without base)
        :data: tata to pass to the request if any
        :returns: requests object

        """

        if self.noEdit and method != 'get':
            return
        pk_user = self.config["partkeepr"]["user"]
        pk_pwd = self.config["partkeepr"]["pwd"]
        pk_url = self.config["partkeepr"]["url"]
        try:
            r = requests.request(
                method,
                pk_url + url,
                **kwargs,
                auth=HTTPBasicAuth(pk_user, pk_pwd),
                verify=False
            )
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            sys.exit(1)

        return r

    def decode_manufacturers(self, manufacturers):
        decoded = []
        for manufacturer in manufacturers:
            try:
                decoded.append({"name": manufacturer["manufacturer"]['name'], "partNumber": manufacturer["partNumber"]})
            except TypeError:
                decoded.append({"name": "", "partNumber": ""})
        return decoded

    def decode_attachments(self, attachments):
        decoded = []
        for attachment in attachments:
            decoded.append({"filename": attachment["originalFilename"],
                            "url": self.config["partkeepr"]["url"] + attachment["@id"] + "/getFile",
                            'description': attachment["description"]})
        return decoded

    def decode_parameters(self, parameters, partname):
        decoded = {}
        for parameter in parameters:
            if parameter["valueType"] == "string":
                decoded[parameter["name"]] = {"value": parameter["stringValue"]}
            elif parameter["valueType"] == "numeric":
                if parameter["unit"] is not None:
                    if parameter["maxSiPrefix"] is not None:
                        maxValue = Decimal(str(parameter["maxValue"])) * Decimal(
                            parameter["maxSiPrefix"]["base"]) ** Decimal(parameter["maxSiPrefix"]["exponent"])
                    else:
                        maxValue = Decimal(str(parameter["maxValue"])) if parameter["maxValue"] is not None else None
                    if parameter["minSiPrefix"] is not None:
                        minValue = Decimal(str(parameter["minValue"])) * Decimal(
                            parameter["minSiPrefix"]["base"]) ** Decimal(parameter["minSiPrefix"]["exponent"])
                    else:
                        minValue = Decimal(str(parameter["minValue"])) if parameter["minValue"] is not None else None
                    if parameter["siPrefix"] is not None:
                        value = Decimal(str(parameter["value"])) * Decimal(parameter["siPrefix"]["base"]) ** Decimal(
                            parameter["siPrefix"]["exponent"])
                    else:
                        value = Decimal(str(parameter["value"])) if parameter["value"] is not None else None
                    decoded[parameter["name"]] = {"value": value, "valueMin": minValue, "valueMax": maxValue,
                                                  "unit": parameter["unit"]["name"]}
                else:
                    value = Decimal(str(parameter["value"])) if parameter["value"] is not None else None
                    maxValue = Decimal(str(parameter["maxValue"])) if parameter["maxValue"] is not None else None
                    minValue = Decimal(str(parameter["minValue"])) if parameter["minValue"] is not None else None
                    decoded[parameter["name"]] = {"value": value, "valueMax": maxValue, "valueMin": minValue}
                    print(parameter)
            else:
                raise
        return decoded

    def decode_part(self, part):
        try:
            footprint_name = part["footprint"]["name"]
        except:
            footprint_name = ""

        decoded = {'name': part['name'], "description": part["description"],
                   "parameters": self.decode_parameters(part["parameters"], part['name']),
                   "attachments": self.decode_attachments(part["attachments"]),
                   "comment": part["comment"], "footprint": footprint_name,
                   "manufacturers": self.decode_manufacturers(part["manufacturers"]),
                   "productionRemarks": part["productionRemarks"], 'partkeepr_id': part['@id']}
        if part['name'] == "CL10A475KP8NNNC":
            print(decoded["parameters"])
        return decoded

    def get_component(self, id):
        params = {"itemsPerPage": 9999}
        r = self.api_call('get', '/api/parts/' + id, params=params)
        return r.json()

    def get_components(self):
        params = {"itemsPerPage": 9999}
        r = self.api_call('get', '/api/parts', params=params)
        rj = r.json()

        with open('partkeepr.json', 'w') as outputfile:
            json.dump(rj, outputfile, sort_keys=True, indent=4)

        resistors = []
        capacitors = []
        inductors = []
        others = []
        for part in rj["hydra:member"]:
            if part["categoryPath"].startswith("Root Category ➤ Resistors"):
                resistors.append(self.decode_part(part))
            elif part["categoryPath"].startswith("Root Category ➤ Capacitors"):
                capacitors.append(self.decode_part(part))
            elif part["categoryPath"].startswith("Root Category ➤ Inductors"):
                inductors.append(self.decode_part(part))
            else:
                others.append(part)

        to_save = [{'filename': 'resistors.json', 'data': resistors},
                   {'filename': 'capacitors.json', 'data': capacitors},
                   {'filename': 'inductors.json', 'data': inductors},
                   {'filename': 'others.json', 'data': others}]
        for s in to_save:
            with open(s['filename'], 'w') as outputfile:
                json.dump(s['data'], outputfile, sort_keys=True, indent=4, cls=DecimalEncoder)

    def __convert_part_response_to_put_request(self, part):
        part.pop('@context')
        part.pop("@id")
        part.pop("averagePrice")
        part.pop("createDate")
        part.pop("lowStock")
        part.pop("stockLevel")
        part.pop("removals")
        for attachment in part["attachments"]:
            attachment["created"] = None
        for parameter in part['parameters']:
            parameter["normalizedMaxValue"] = None
            parameter["normalizedMinValue"] = None
            parameter["normalizedValue"] = None
        part["partPartKeeprPartBundleEntityMetaPartParameterCriterias"] = []
        part["partPartKeeprPartBundleEntityPartAttachments"] = []
        part["partPartKeeprPartBundleEntityPartDistributors"] = []
        part["partPartKeeprPartBundleEntityPartManufacturers"] = []
        part["partPartKeeprPartBundleEntityPartParameters"] = []
        part["partPartKeeprProjectBundleEntityProjectParts"] = []
        part["partPartKeeprProjectBundleEntityProjectRunParts"] = []
        part["partPartKeeprProjectBundleEntityReportParts"] = []
        part["partPartKeeprStockBundleEntityStockEntries"] = []
        part["projectParts"] = []
        part["stockLevels"] = []
        part['category'] = self.__update_category_fields(part['category'])
        part['storageLocation']['category'] = self.__update_category_fields(part['storageLocation']['category'])
        return part

    def __update_category_fields(self, category):
        category["allowDrag"] = True
        category["allowDrop"] = True
        category["checked"] = None
        category["children"] = None
        category["cls"] = ""
        category["depth"] = 0
        category["parentId"] = None
        category["qshowDelay"] = 0
        category["qtip"] = ""
        category["qtitle"] = ""
        category["rgt"] = 0
        category["root"] = None
        category["text"] = ""
        category["visible"] = True
        category["expandable"] = True
        category["glyph"] = ""
        category["href"] = ""
        category["hrefTarget"] = ""
        category["icon"] = ""
        category["iconCls"] = ""
        category["index"] = -1
        category["isFirst"] = False
        category["isLast"] = False
        category["leaf"] = False
        category["lft"] = 0
        category["loaded"] = False
        category["loading"] = False
        category["lvl"] = 0
        return category

    def debug_log(self, **kwargs):
        if self.debug is True:
            print(kwargs)
