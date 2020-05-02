from .part import Part
from decimal import Decimal
import json
import sys

sys.path.insert(1, "third_party/partname-resolver")
from partname_resolver.components.resistor import Resistor
from partname_resolver.components.inductor import Inductor
from partname_resolver.units.resistance import Resistance #, ResistanceRange todo will be needed for potentiometers
from partname_resolver.units.resistanceTolerance import Tolerance as ResistanceTolerance
from partname_resolver.units.inductance import Inductance
from partname_resolver.units.resistanceTolerance import Tolerance as InductanceTolerance
from partname_resolver.units.current import Current
from partname_resolver.units.temperature import TemperatureRange


def working_voltage_parameter_to_unit(part):
    voltage = part.get_parameter('voltage')
    return None


def resistance_tolerance_from_from_part(part):
    """Convert partkeepr part tolerance parameter to Tolerance object"""
    for parameter in part.request['parameters']:
        if parameter["valueType"] == "numeric" and parameter['name'] == 'Tolerance':
            decoded = decode_parameter(parameter)
            if 'unit' in decoded and decoded["unit"] == 'Ohm':
                if decoded['value'] is not None:
                    return ResistanceTolerance(decoded["value"])
                else:
                    return ResistanceTolerance(decoded["valueMin"], decoded["valueMax"])
            else:
                if decoded['value'] is not None:
                    return ResistanceTolerance(str(decoded['value']) + "%")
                else:
                    return ResistanceTolerance(str(decoded["valueMin"]) + "%", "+" + str(decoded["valueMax"]) + "%")


def inductance_tolerance_from_from_part(part):
    """Convert partkeepr part tolerance parameter to Tolerance object"""
    for parameter in part.request['parameters']:
        if parameter["valueType"] == "numeric" and parameter['name'] == 'Tolerance':
            decoded = decode_parameter(parameter)
            if 'unit' in decoded and decoded["unit"] == 'Henry':
                if decoded['value'] is not None:
                    return InductanceTolerance(decoded["value"])
                else:
                    return InductanceTolerance(decoded["valueMin"], decoded["valueMax"])
            else:
                if decoded['value'] is not None:
                    return InductanceTolerance(str(decoded['value']) + "%")
                else:
                    return InductanceTolerance(str(decoded["valueMin"]) + "%", "+" + str(decoded["valueMax"]) + "%")


def power_parameter_to_unit(part):
    return None


def working_temperature_range_from_part(part):
    for parameter in part.request['parameters']:
        if parameter["valueType"] == "numeric":
            if 'Working Temperature' == parameter['name']:
                decoded = decode_parameter(parameter)
                return TemperatureRange(decoded['valueMin'], decoded['valueMax'])


def resistance_paremeter_to_unit(part):
    return None


def inductance_from_part(part):
    for parameter in part.request['parameters']:
        if parameter["valueType"] == "numeric" and parameter['name'] == "Capacitance":
            decoded = decode_parameter(parameter)
            if decoded is not None:
                return Inductance(decoded['value'])
            else:
                return InductanceRange(decoded["valueMin"], decoded["valueMax"])


def quality_from_part(part):
    for parameter in part.request['parameters']:
        if parameter["valueType"] == "numeric" and parameter['name'] == "Q":
            decoded = decode_parameter(parameter)
            if decoded is not None:
                return decoded['value']
            #else:
            #    return InductanceRange(decoded["valueMin"], decoded["valueMax"])


def rated_current_from_part(part):
    for parameter in part.request['parameters']:
        if parameter["valueType"] == "numeric" and parameter['name'] == "Rated Current":
            decoded = decode_parameter(parameter)
            if decoded is not None:
                return Current(decoded['value'])
            #else:
            #    return InductanceRange(decoded["valueMin"], decoded["valueMax"])


def inductor_type_from_part(part):
    for parameter in part.request['parameters']:
        if parameter["valueType"] == "string" and parameter['name'] == "Part Type":
            decoded = decode_parameter(parameter)
            if decoded is not None:
                return Inductor.Type(decoded['value'])


def SRF_current_from_part(part):
    for parameter in part.request['parameters']:
        if parameter["valueType"] == "numeric" and parameter['name'] == "Self Resonant Frequency":
            decoded = decode_parameter(parameter)
            if decoded is not None:
                return decoded['value']
            #else:
            #    return InductanceRange(decoded["valueMin"], decoded["valueMax"])


def voltage_max_from_part(part):
    for parameter in part.request['parameters']:
        if parameter["valueType"] == "numeric" and parameter['name'] == "Voltage":
            decoded = decode_parameter(parameter)
            if decoded is not None:
                return decoded['valueMax']
            #else:
            #    return InductanceRange(decoded["valueMin"], decoded["valueMax"])


def resistance_from_part(part):
    for parameter in part.request['parameters']:
        if parameter["valueType"] == "numeric" and parameter['name'] == "Resistance":
            decoded = decode_parameter(parameter)
            if decoded is not None:
                return Resistance(decoded['value'])
            else:
                return ResistanceRange(decoded["valueMin"], decoded["valueMax"])

def to_resistor(part):
    return Resistor(resistor_type=None,
                    manufacturer=part.get_manufacturer_name(),
                    partnumber=part.get_manufacturer_part_number(),
                    working_temperature_range=temperature_range_to_unit(part),
                    series=None,
                    resistance=resistance_paremeter_to_unit(part),
                    power=power_parameter_to_unit(part),
                    max_working_voltage=working_voltage_parameter_to_unit(part),
                    tolerance=None,
                    case=part.get_footprint(),
                    note=part.get_comment())


def part_to_inductor(part):
    if len(part.get_manufacturers()) > 1:
        raise ValueError("Part has more than one manufacturer")
    manufacturer = part.get_manufacturers()[0] if len(part.get_manufacturers()) == 1 else None

    return Inductor(inductor_type=inductor_type_from_part(part),
                    manufacturer=manufacturer['manufacturer']['name'] if 'name' in manufacturer['manufacturer'] else None,
                    partnumber=manufacturer['partNumber'],
                    working_temperature_range=working_temperature_range_from_part(part),
                    series=None,
                    inductance=inductance_from_part(part),
                    tolerance=inductance_tolerance_from_from_part(part),
                    q=quality_from_part(part),
                    dc_resistance=resistance_from_part(part),
                    rated_current=rated_current_from_part(part),
                    self_resonant_frequency=SRF_current_from_part(part),
                    max_working_voltage=voltage_max_from_part(part),
                    case=part.get_footprint()['name'] if part.get_footprint() is not None else None,
                    note=part.get_comment())


def decode_parameter(parameter):
    if parameter["valueType"] == "string":
        decoded = {"value": parameter["stringValue"]}
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
            decoded = {"value": value, "valueMin": minValue, "valueMax": maxValue,
                                          "unit": parameter["unit"]["name"]}
        else:
            value = Decimal(str(parameter["value"])) if parameter["value"] is not None else None
            maxValue = Decimal(str(parameter["maxValue"])) if parameter["maxValue"] is not None else None
            minValue = Decimal(str(parameter["minValue"])) if parameter["minValue"] is not None else None
            decoded = {"value": value, "valueMax": maxValue, "valueMin": minValue}
    else:
        raise
    return decoded
