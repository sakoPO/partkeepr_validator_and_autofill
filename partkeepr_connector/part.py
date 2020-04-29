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

    def get_description(self):
        return self.request['description']

    def set_description(self, description):
        self.request['description'] = description if description is not None else ""

    def add_parameter(self, name, value, description=None):
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
                    parameter['value'] = value.get_value()
                    # todo Add support for si prefixes
                else:
                    parameter['value'] = value.get_value()
            elif isinstance(value, RangeBase):
                parameter['valueType'] = 'numeric'
                min = value.min.get_value()
                max = value.max.get_value()
                if value.min.name is not None:
                    unit = self.units.get(value.min.name)
                    if unit is None:
                        raise ValueError
                    parameter["unit"] = unit
                    parameter['minValue'] = int(min) if float(min).is_integer() else float(min)
                    parameter['maxValue'] = int(max) if float(max).is_integer() else float(max)
                    # todo Add support for si prefixes
                else:
                    parameter['minValue'] = int(min) if float(min).is_integer() else float(min)
                    parameter['maxValue'] = int(max) if float(max).is_integer() else float(max)
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
