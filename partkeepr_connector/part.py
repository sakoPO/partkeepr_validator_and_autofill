from .partkeepr_units import Units as PartkeeprUnits
import sys

sys.path.insert(1, "third_party/partname-resolver")

from partname_resolver.units.unit_base import Unit
from partname_resolver.units.range_base import RangeBase


class Part:
    parameter_template = {
        "valueType": "numeric",
        "name": "",
        "description": "",
        "value": None,
        "normalizedValue": None,
        "maxValue": None,
        "normalizedMaxValue": None,
        "minValue": None,
        "normalizedMinValue": None,
        "stringValue": "",
        "unit": None,
        "siPrefix": None,
        "minSiPrefix": None,
        "maxSiPrefix": None}

    def __init__(self, id, request, units):
        self.id = id
        self.request = request
        self.units = units

    def get_id(self):
        return self.id

    def get_name(self):
        return self.request['name']

    def get_manufacturers(self):
        return self.request['manufacturers']

    def add_manufacturer_and_partnumber(self, manufacturer, partnumber):
        pass

    def set_comment(self, comment):
        self.request['comment'] = comment if comment is not None else ""

    def get_comment(self):
        return self.request['comment']

    def get_description(self):
        return self.request['description']

    def set_description(self, description):
        if isinstance(description, str):
            self.request['description'] = description if description is not None else ""
        else:
            raise TypeError

    def get_footprint(self):
        return self.request['footprint']

    def set_footprint(self):
        pass

    def add_parameter(self, name, value, numeric_value_field='value', description=None):
        def decimal_to_int_or_float(parameter_value):
            return int(parameter_value) if float(parameter_value).is_integer() else float(parameter_value)

        value_to_si_prefix = {'value': 'siPrefix', 'minValue': 'minSiPrefix', 'maxValue': 'maxSiPrefix'}
        if self.has_parameter(name) is False:
            parameter = dict(Part.parameter_template)
            parameter['name'] = name
            parameter['description'] = description if description is not None else ""
            if isinstance(value, str):
                parameter['valueType'] = 'string'
                parameter['stringValue'] = value
            elif isinstance(value, Unit):
                parameter['valueType'] = 'numeric'
                if value.name is not None:
                    unit = self.units.get(value.name)
                    if unit is None:
                        raise ValueError
                    parameter["unit"] = unit
                    prefix = value.get_closest_prefix(self.units.get_supported_prefixes(unit)['names'])
                    parameter[numeric_value_field] = decimal_to_int_or_float(value.get_value_as(prefix))
                    parameter[value_to_si_prefix[numeric_value_field]] = self.units.get_prefix(unit, prefix)
                else:
                    parameter[numeric_value_field] = decimal_to_int_or_float(value.get_value())
            elif isinstance(value, RangeBase):
                parameter['valueType'] = 'numeric'
                min = value.min.get_value() if isinstance(value.min, Unit) else value.min
                max = value.max.get_value() if isinstance(value.max, Unit) else value.max
                if isinstance(value.min, Unit) and value.min.name is not None:
                    unit = self.units.get(value.min.name)
                    if unit is None:
                        raise ValueError
                    parameter["unit"] = unit
                    min_prefix = value.min.get_closest_prefix(self.units.get_supported_prefixes(unit)['names'])
                    parameter['minValue'] = decimal_to_int_or_float(value.min.get_value_as(min_prefix))
                    parameter['minSiPrefix'] = self.units.get_prefix(unit, min_prefix)

                    max_prefix = value.max.get_closest_prefix(self.units.get_supported_prefixes(unit)['names'])
                    parameter['maxValue'] = decimal_to_int_or_float(value.max.get_value_as(max_prefix))
                    parameter['maxSiPrefix'] = self.units.get_prefix(unit, max_prefix)
                else:
                    parameter['minValue'] = decimal_to_int_or_float(min)
                    parameter['maxValue'] = decimal_to_int_or_float(max)
            else:
                raise TypeError
            self.request['parameters'].insert(0, parameter)
            return True
        return False

    def get_parameter(self, name):
        for parameter in self.request['parameters']:
            if name in parameter['name']:
                return parameter

    def has_parameter(self, parameter_name):
        for parameter in self.request['parameters']:
            if parameter_name in parameter['name']:
                return True
        return False
