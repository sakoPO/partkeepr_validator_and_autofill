from partkeepr_connector.partkeepr import Partkeepr
import configparser
import unittest
from capacitors_test import *
from resistors_test import *

config = configparser.ConfigParser()
config.read("config.ini")
partkeepr = Partkeepr(config)
partkeepr.get_components()

if __name__ == '__main__':
    unittest.main()
