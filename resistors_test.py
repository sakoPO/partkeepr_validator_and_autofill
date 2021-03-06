from common import *
from unittest import TestCase
import json
import skip_resistors_test
import sys

sys.path.insert(1, "third_party/partname-resolver")
from partname_resolver.resistors import resistors_partname_decoder
from partname_resolver.units.resistance import Resistance
from partname_resolver.units.power import Power


class TestResistors(TestCase):
    @classmethod
    def setUpClass(cls):
        with open("resistors.json") as file:
            cls.resistors = json.load(file)

    def test_has_resistance_parameter(self):
        for resistor in self.resistors:
            with self.subTest(resistor['name']):
                if resistor['partkeepr_id'] in skip_resistors_test.test_has_resistance_parameter:
                    self.skipTest(str(resistor['name']) + " part in skip list")
                self.assertIn("Resistance", resistor["parameters"])
                resistance = resistor["parameters"]["Resistance"]
                self.assertIsNotNone(resistance["value"])
                self.assertEqual(resistance["unit"], "Ohm")

    def test_has_tolerance_parameter(self):
        for resistor in self.resistors:
            with self.subTest(resistor['name']):
                if resistor['partkeepr_id'] in skip_resistors_test.test_has_tolerance_parameter:
                    self.skipTest(str(resistor['name']) + " part in skip list")
                self.assertIn("Tolerance", resistor["parameters"])
                tolerance = resistor["parameters"]["Tolerance"]
                self.assertIsNotNone(tolerance["value"])

    def test_has_voltage_parameter(self):
        for resistor in self.resistors:
            with self.subTest(resistor['name'] + " (" + resistor['partkeepr_id'].replace("/api/parts/", "") + ")"):
                if resistor['partkeepr_id'] in skip_resistors_test.test_has_voltage_parameter:
                    self.skipTest(str(resistor['name']) + " part in skip list")
                self.assertIn("Voltage", resistor["parameters"])
                self.assertIsNotNone(resistor["parameters"]['Voltage']['valueMax'])

    def test_has_power_parameter(self):
        for resistor in self.resistors:
            with self.subTest(resistor['name']):
                if resistor['partkeepr_id'] in skip_resistors_test.test_has_power_parameter:
                    self.skipTest(str(resistor['name']) + " part in skip list")
                self.assertIn("Power", resistor["parameters"])
                power = resistor["parameters"]["Power"]
                self.assertEqual(power["unit"], "Watt")
                self.assertIsNone(power["value"])
                self.assertIsNone(power["valueMin"])
                self.assertIsNotNone(power["valueMax"])

    def test_description_format(self):
        for resistor in self.resistors:
            with self.subTest(resistor['name']):
                res = None
                if len(resistor['manufacturers']):
                    manufacturer_part_number = resistor["manufacturers"][0]['partNumber']
                    res = resistors_partname_decoder.resolve(manufacturer_part_number)
                if res is None:
                    res = resistor_from_partkeepr_json(resistor)
                self.assertIsNotNone(res)
                self.assertEqual(res.get_description(), resistor["description"])

    def test_parameters_equal_decoded_parameters_from_partname(self):
        for resistor in self.resistors:
            if len(resistor['manufacturers']):
                manufacturer_part_number = resistor["manufacturers"][0]['partNumber']
                if len(manufacturer_part_number) == 0:
                    continue
                with self.subTest(resistor['name']):
                    if resistor[
                        'partkeepr_id'] in skip_resistors_test.test_parameters_equal_decoded_parameters_from_partname:
                        self.skipTest(str(resistor['name']) + " part in skip list")
                    parameters = resistor["parameters"]
                    tolerance = tolerance_from_partkeepr_json(parameters["Tolerance"])
                    working_temperature = working_temperature_range_from_partkeepr_json(parameters)
                    decoded_parameters = resistors_partname_decoder.resolve(manufacturer_part_number)
                    self.assertIsNotNone(decoded_parameters)
                    self.assertEqual(Resistance(parameters["Resistance"]["value"]), decoded_parameters.resistance)
                    self.assertEqual(Power(parameters["Power"]["valueMax"]), decoded_parameters.power)
                    self.assertEqual(tolerance, decoded_parameters.tolerance)
                    self.assertEqual(decoded_parameters.max_working_voltage,
                                     str(parameters['Voltage']['valueMax']) + "V")
                    if working_temperature is not None:
                        self.assertEqual(decoded_parameters.working_temperature_range, working_temperature)
