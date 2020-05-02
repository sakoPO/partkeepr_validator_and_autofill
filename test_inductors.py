import unittest
from common import *
import json
import skip_resistors_test
import sys

sys.path.insert(1, "third_party/partname-resolver")
from partname_resolver.inductors import inductors_partname_decoder
from partname_resolver.units.inductance import Inductance
#from partname_resolver.units.power import Power


class InductorsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("inductors.json") as file:
            cls.inductors = json.load(file)

    def test_inductance_parameter(self):
        for inductor in self.inductors:
            with self.subTest(inductor['name']):
                if inductor['partkeepr_id'] in skip_resistors_test.test_has_resistance_parameter:
                    self.skipTest(str(inductor['name']) + " part in skip list")
                self.assertIn("Inductance", inductor["parameters"])
                resistance = inductor["parameters"]["Inductance"]
                self.assertIsNotNone(resistance["value"])
                self.assertEqual(resistance["unit"], "Henry")

    def test_description_format(self):
        for inductor in self.inductors:
            with self.subTest(inductor['name']):
                res = None
                if len(inductor['manufacturers']):
                    manufacturer_part_number = inductor["manufacturers"][0]['partNumber']
                    res = inductors_partname_decoder.resolve(manufacturer_part_number)
                if res is None:
                    res = inductor_from_partkeepr_json(inductor)
                self.assertIsNotNone(res)
                self.assertEqual(res.get_description(), inductor["description"])

    def test_parameters_equal_decoded_parameters_from_partname(self):
        for inductor in self.inductors:
            if len(inductor['manufacturers']):
                manufacturer_part_number = inductor["manufacturers"][0]['partNumber']
                if len(manufacturer_part_number) == 0:
                    continue
                with self.subTest(inductor['name']):
                    if inductor[
                        'partkeepr_id'] in skip_resistors_test.test_parameters_equal_decoded_parameters_from_partname:
                        self.skipTest(str(inductor['name']) + " part in skip list")
                    decoded_parameters = inductors_partname_decoder.resolve(manufacturer_part_number)
                    self.assertIsNotNone(decoded_parameters)
                    parameters = inductor["parameters"]
                    self.assertEqual(decoded_parameters.inductance, Inductance(parameters["Inductance"]["value"]))
                    tolerance = tolerance_from_partkeepr_json(parameters["Tolerance"])
                    self.assertEqual(decoded_parameters.tolerance, tolerance)
                    working_temperature = working_temperature_range_from_partkeepr_json(parameters)
                    self.assertEqual(decoded_parameters.max_working_voltage,
                                     str(parameters['Voltage']['valueMax']) + "V")
                    #self.assertEqual(Power(parameters["Power"]["valueMax"]), decoded_parameters.power)

                    if working_temperature is not None:
                        self.assertEqual(decoded_parameters.working_temperature_range, working_temperature)

if __name__ == '__main__':
    unittest.main()
