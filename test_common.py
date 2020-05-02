import unittest
from common import *
import json
import skip_resistors_test
import sys


class CommonTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("inductors.json") as file:
            cls.components = json.load(file)
        with open("resistors.json") as file:
            cls.components += json.load(file)
        with open("capacitors.json") as file:
            cls.components += json.load(file)
        #with open("others.json") as file:
        #    cls.inductors += json.load(file)

    def test_single_manufacturer_per_part(self):
        for component in self.components:
            with self.subTest(component['name']):
                if component['partkeepr_id'] in skip_resistors_test.test_single_manufacturer_per_part:
                    self.skipTest("part in skip list")
                self.assertEqual(len(component["manufacturers"]), 1)

    def test_part_name_equal_manufacturer_part_name(self):
        for component in self.components:
            with self.subTest(component['name']):
                if len(component["manufacturers"]) > 0:
                    self.assertEqual(component["name"], component["manufacturers"][0]["partNumber"])

    def test_has_production_remarks(self):
        for component in self.components:
            with self.subTest(component['name']):
                self.assertIn(component["productionRemarks"], ["SMD", "SMT", "THT", "Screw"])

    def test_working_temperature_parameter(self):
        for component in self.components:
            with self.subTest(component['name'] + " (" + component['partkeepr_id'] + ')'):
                if component['partkeepr_id'] in skip_resistors_test.test_working_temperature_parameter:
                    self.skipTest(str(component['name']) + " part in skip list")
                self.assertIn("Working Temperature", component["parameters"])
                working_temperature = component["parameters"]["Working Temperature"]
                self.assertEqual(working_temperature["unit"], "Celsius")
                self.assertIsNone(working_temperature["value"])
                self.assertIsNotNone(working_temperature["valueMin"])
                self.assertIsNotNone(working_temperature["valueMax"])

    def test_footprint(self):
        for component in self.components:
            with self.subTest(component['name']):
                if component["productionRemarks"] == "THT":
                    self.assertTrue(True)
                elif component["productionRemarks"] == "SMD":
                    self.assertIn(component["footprint"], ["0402", "0603", "0805", "1206", "2512"])


if __name__ == '__main__':
    unittest.main()
