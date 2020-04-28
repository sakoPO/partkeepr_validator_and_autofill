from unittest import TestCase
import json
import decimal
from common import *
import skip_capacitors_test
import sys

sys.path.insert(1, "third_party/partname-resolver")

from partname_resolver.capacitors.capacitor import Capacitor
from partname_resolver.units.capacitance import Capacitance, CapacitanceRange
import partname_resolver.capacitors.capacitors_partname_decoder as capacitorPartname


class TestCapacitors(TestCase):
    @classmethod
    def setUpClass(cls):
        with open("capacitors.json") as file:
            cls.capacitors = json.load(file, parse_float=decimal.Decimal)

    def test_single_manufacturer_per_part(self):
        for capacitor in self.capacitors:
            with self.subTest(capacitor['name']):
                if capacitor['partkeepr_id'] in skip_capacitors_test.test_single_manufacturer_per_part:
                    self.skipTest("part in skip list")
                self.assertEqual(len(capacitor["manufacturers"]), 1)

    def test_part_name_equal_manufacturer_part_name(self):
        for resistor in self.capacitors:
            with self.subTest(resistor['name']):
                if len(resistor["manufacturers"]) > 0:
                    self.assertEqual(resistor["name"], resistor["manufacturers"][0]["partNumber"])

    def test_has_production_remarks(self):
        for resistor in self.capacitors:
            with self.subTest(resistor['name']):
                self.assertIn(resistor["productionRemarks"], ["SMD", "SMT", "THT", "Screw"])

    def test_has_capacitance_parameter(self):
        for resistor in self.capacitors:
            with self.subTest(resistor['name']):
                self.assertIn("Capacitance", resistor["parameters"])
                capacitance = resistor["parameters"]["Capacitance"]
                if capacitance["valueMin"] is not None or capacitance['valueMax'] is not None:
                    self.assertIsNotNone(capacitance["valueMin"])
                    self.assertIsNotNone(capacitance["valueMax"])
                else:
                    self.assertIsNotNone(capacitance["value"])
                self.assertEqual(capacitance["unit"], "Farad")

    def test_has_tolerance_parameter(self):
        for resistor in self.capacitors:
            with self.subTest(resistor['name']):
                self.assertIn("Tolerance", resistor["parameters"])
                self.assertIsNotNone(capacitanceTolerance_from_partkeepr_json(resistor["parameters"]["Tolerance"]))

    def test_has_voltage_parameter(self):
        for capacitor in self.capacitors:
            with self.subTest(capacitor['name'] + " (" + capacitor['partkeepr_id'].replace('/api/parts/', '') + ')'):
                if capacitor['partkeepr_id'] in skip_capacitors_test.test_has_voltage_parameter:
                    self.skipTest("part in skip list")
                self.assertIn("Voltage", capacitor["parameters"])

    def test_has_capacitor_type_parameter(self):
        for resistor in self.capacitors:
            with self.subTest(resistor['name']):
                self.assertIn("Capacitor Type", resistor["parameters"])

    def test_footprint(self):
        for resistor in self.capacitors:
            with self.subTest(resistor['name']):
                if resistor["productionRemarks"] == "THT":
                    self.assertTrue(True)
                elif resistor["productionRemarks"] == "SMD":
                    self.assertIn(resistor["footprint"], ["0402", "0603", "0805", "1206", "1210", "2512"])

    def test_description_format(self):
        for capacitor in self.capacitors:
            with self.subTest(capacitor['name']):
                if len(capacitor['manufacturers']):
                    manufacturer_part_number = capacitor["manufacturers"][0]['partNumber']
                    cap = capacitorPartname.resolve(manufacturer_part_number)
                else:
                    cap = capacitor_from_partkeepr_json(capacitor)
                self.assertIsNotNone(cap)
                self.assertEqual(cap.get_description(), capacitor["description"])

    def test_parameters_equal_decoded_parameters_from_partname(self):
        for capacitor in self.capacitors:
            if len(capacitor['manufacturers']):
                manufacturer_part_number = capacitor["manufacturers"][0]['partNumber']
                if len(manufacturer_part_number) == 0:
                    continue
                with self.subTest(capacitor['name']):
                    parameters = capacitor["parameters"]
                    tolerance = capacitanceTolerance_from_partkeepr_json(capacitor["parameters"]["Tolerance"])
                    decoded_parameters = capacitorPartname.resolve(manufacturer_part_number)
                    self.assertIsNotNone(decoded_parameters)
                    self.assertEqual(Capacitance(decimal.Decimal(parameters["Capacitance"]["value"])),
                                     decoded_parameters.capacitance)
                    self.assertEqual(parameters["Voltage"]["value"] + "V",
                                     decoded_parameters.voltage.replace("DC", ""))
                    self.assertEqual(parameters["Dielectric Type"]["value"], decoded_parameters.dielectric_type)
                    self.assertEqual(tolerance, decoded_parameters.tolerance)
                    # cap = Capacitor(capacitor_type=parameters["Capacitor type"],
                    #                manufacturer=capacitor["manufacturers"][0]['name'],
                    #                partnumber=manufacturer_part_number,
                    #                series='',
                    #                capacitance=parameters["Capacitance"]["value"],
                    #                voltage=parameters["Voltage"],
                    #                tolerance=parameters['Tolerance'],
                    #                dielectric_type=parameters['Dielectric Type'],
                    #                case=capacitor['footprint'],
                    #                note="")
                    # self.assertEqual(decoded_parameters, cap)

