import configparser
import json
import skip_autofill
from common import *
from partkeepr_connector.partkeepr import Partkeepr
import sys

sys.path.insert(1, "third_party/partname-resolver")
from partname_resolver.resistors import resistors_partname_decoder
from partname_resolver.capacitors import capacitors_partname_decoder


class AutofillDescription:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.partkeepr = Partkeepr(config)
        self.partkeepr.get_components()  # this will create resistors.json and capacitors.json
        with open("resistors.json") as file:
            self.resistors = json.load(file)
        with open("capacitors.json") as file:
            self.capacitors = json.load(file)

    def autofill_resistors_description(self):
        for resistor in self.resistors:
            if resistor['partkeepr_id'] in skip_autofill.autofill_description:
                print("Skipping description update of part: ", resistor['partkeepr_id'], " found in skip list.")
                continue
            if len(resistor['manufacturers']):
                manufacturer_part_number = resistor["manufacturers"][0]['partNumber']
                resistor_from_partname = resistors_partname_decoder.resolve(manufacturer_part_number)
            else:
                resistor_from_partname = None
            resistor_from_parameters = resistor_from_partkeepr_json(resistor)
            if resistor_from_partname is not None:
                if resistor_from_parameters.partial_compare(resistor_from_partname):
                    if resistor["description"] != resistor_from_partname.get_description():
                        self.partkeepr.set_part_description(resistor["partkeepr_id"],
                                                            resistor_from_partname.get_description())
                else:
                    print("Unable to update description, part parameters are different than parameters from part name")
                    print("From part name:", resistor_from_partname)
                    print("From parameters:", resistor_from_parameters)
            else:
                if resistor["description"] != resistor_from_parameters.get_description():
                    self.partkeepr.set_part_description(resistor["partkeepr_id"],
                                                        resistor_from_parameters.get_description())

    def autofill_capacitors_description(self):
        for capacitor in self.capacitors:
            if capacitor['partkeepr_id'] in skip_autofill.autofill_description:
                print("Skipping description update of part: ", capacitor['partkeepr_id'], " found in skip list.")
                continue
            if len(capacitor['manufacturers']):
                manufacturer_part_number = capacitor["manufacturers"][0]['partNumber']
                capacitor_from_partname = capacitors_partname_decoder.resolve(manufacturer_part_number)
            else:
                capacitor_from_partname = None
            capacitor_from_parameters = capacitor_from_partkeepr_json(capacitor)
            if capacitor_from_partname is not None:
                if capacitor_from_parameters.partial_compare(capacitor_from_partname, debug=True):
                    if capacitor["description"] != capacitor_from_partname.get_description():
                        print("Updating description, from:", capacitor["description"], ", to:",
                              capacitor_from_parameters.get_description())
                        self.partkeepr.set_part_description(capacitor["partkeepr_id"],
                                                            capacitor_from_partname.get_description())
                else:
                    print("Unable to update description, part parameters are different than parameters from part name")
                    print("\tFrom part name:", capacitor_from_partname)
                    print("\tFrom parameters:", capacitor_from_parameters)
            else:
                if capacitor["description"] != capacitor_from_parameters.get_description():
                    print("Updating description, from:", capacitor["description"], ", to:",
                          capacitor_from_parameters.get_description())
                    self.partkeepr.set_part_description(capacitor["partkeepr_id"],
                                                        capacitor_from_parameters.get_description())

    def edit_power_parameter(self):
        for resistor in self.resistors:
            if resistor['partkeepr_id'] in skip_autofill.autofill_description:
                print("Skipping parameter update of part: ", resistor['partkeepr_id'], " found in skip list.")
                continue
            if len(resistor['manufacturers']):
                manufacturer_part_number = resistor["manufacturers"][0]['partNumber']
                resistor_from_partname = resistors_partname_decoder.resolve(manufacturer_part_number)
                if resistor_from_partname is not None:
                    resistor_from_parameters = resistor_from_partkeepr_json(resistor)
                    if resistor_from_partname.power != resistor_from_parameters.power:
                        print("Updating power parameter at: ", resistor['partkeepr_id'], "from: ",
                              resistor_from_parameters.power, " to: ", resistor_from_partname.power)
                        new_value = {'value': None,
                                     'minValue': None,
                                     'maxValue': resistor_from_partname.power}
                        self.partkeepr.edit_part_parameter(resistor['partkeepr_id'], "Power", new_value)

# test = AutofillDescription()
# test.autofill_resistors_description()
# test.autofill_capacitors_description()
# test.edit_power_parameter()
