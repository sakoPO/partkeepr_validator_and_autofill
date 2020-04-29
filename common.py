from decimal import Decimal
import sys

sys.path.insert(1, "third_party/partname-resolver")
from partname_resolver.resistors.resistor import Resistor
from partname_resolver.units.resistanceTolerance import Tolerance as ResistanceTolerance
from partname_resolver.units.temperature import TemperatureRange
from partname_resolver.units.capacitanceTolerance import Tolerance as CapacitanceTolerance
from partname_resolver.capacitors.capacitor import Capacitor
from partname_resolver.units.capacitance import Capacitance, CapacitanceRange


def tolerance_from_partkeepr_json(tolerance_json):
    """Convert partkeepr json tolerance parameter to Tolerance object"""
    if 'unit' in tolerance_json and tolerance_json["unit"] == 'Ohm':
        return ResistanceTolerance(str(tolerance_json["value"]) + "R")
    else:
        if tolerance_json['value'] is not None:
            return ResistanceTolerance(str(tolerance_json["value"]) + "%")
        else:
            return ResistanceTolerance(str(tolerance_json["valueMin"]) + "%", "+" + str(tolerance_json["valueMax"]) + "%")


def working_temperature_range_from_partkeepr_json(parameters):
    if 'Working Temperature' in parameters:
        working_temperature = TemperatureRange(Decimal(parameters['Working Temperature']['valueMin']),
                                               Decimal(parameters['Working Temperature']['valueMax']))
        return working_temperature


def resistor_from_partkeepr_json(resistor_json):
    parameters = resistor_json["parameters"]
    if len(resistor_json["manufacturers"]) > 0:
        part_number = resistor_json["manufacturers"][0]['partNumber']
        manufacturer_name = resistor_json["manufacturers"][0]['name']
    else:
        part_number = resistor_json['name']
        manufacturer_name = None
    if 'Part Type' in parameters:
        resistor_type = Resistor.Type(parameters["Part Type"]['value'])
    else:
        resistor_type = None  # Resistor.Type.ThinFilmResistor  # Resistor.Type(parameters["Resistor Type"]['value'])
    working_temperature = working_temperature_range_from_partkeepr_json(parameters)
    resistance = parameters["Resistance"]["value"]
    tolerance = tolerance_from_partkeepr_json(parameters['Tolerance']) if 'Tolerance' in parameters else None
    return Resistor(resistor_type=resistor_type,
                    manufacturer=manufacturer_name,
                    partnumber=part_number,
                    working_temperature_range=working_temperature,
                    series=None,
                    resistance=resistance,
                    tolerance=tolerance,
                    power=parameters["Power"]['valueMax'] if 'Power' in parameters else None,
                    max_working_voltage=parameters["Voltage"]['valueMax'] + "V" if 'Voltage' in parameters else None,
                    case=resistor_json['footprint'],
                    note="")


def capacitanceTolerance_from_partkeepr_json(tolerance_json):
    """Convert partkeepr json tolerance parameter to Tolerance object"""
    if 'unit' in tolerance_json and tolerance_json["unit"] == 'Farad':
        return CapacitanceTolerance(str(tolerance_json["value"]) + "F")
    else:
        if tolerance_json['value'] is not None:
            return CapacitanceTolerance(str(tolerance_json["value"]) + "%")
        else:
            return CapacitanceTolerance(str(tolerance_json["valueMin"]) + "%", "+" + str(tolerance_json["valueMax"]) + "%")


def capacitance_from_partkeepr_parameters(parameters):
    if "Capacitance" in parameters:
        if parameters["Capacitance"]['value'] is not None:
            return Capacitance(parameters["Capacitance"]['value'])
        else:
            return CapacitanceRange(parameters["Capacitance"]["valueMin"], parameters["Capacitance"]["valueMax"])


def capacitor_from_partkeepr_json(capacitor_json):
    try:
        parameters = capacitor_json["parameters"]
        if len(capacitor_json["manufacturers"]) > 0:
            part_number = capacitor_json["manufacturers"][0]['partNumber']
            manufacturer_name = capacitor_json["manufacturers"][0]['name']
        else:
            part_number = capacitor_json['name']
            manufacturer_name = None
        capacitor_type = Capacitor.Type(parameters["Capacitor Type"]['value'])
        capacitance = capacitance_from_partkeepr_parameters(parameters)
        working_temperature = working_temperature_range_from_partkeepr_json(parameters)
        if 'Voltage' in parameters:
            if parameters['Voltage']['valueMax'] is not None:
                voltage = parameters['Voltage']['valueMax'] + "V"
            else:
                voltage = parameters["Voltage"]['value'] + 'V'
        else:
            voltage = None
        return Capacitor(capacitor_type=capacitor_type,
                         manufacturer=manufacturer_name,
                         partnumber=part_number,
                         working_temperature_range=working_temperature,
                         series=None,
                         capacitance=capacitance,
                         voltage=voltage,
                         tolerance=capacitanceTolerance_from_partkeepr_json(parameters['Tolerance']) if 'Tolerance' in parameters else None,
                         dielectric_type=parameters['Dielectric Type']['value'] if 'Dielectric Type' in parameters else None,
                         case=capacitor_json['footprint'] if len(capacitor_json['footprint']) > 0 else None,
                         note="")
    except TypeError:
        print(capacitor_json)
        raise
