import os
import unittest
import json
from netdiff.batman import BatmanParser


__all__ = ['TestBatmanParser']


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
iulinet = open('{0}/batman.json'.format(CURRENT_DIR)).read()
iulinet2 = open('{0}/batman-1+1.json'.format(CURRENT_DIR)).read()


class TestBatmanParser(unittest.TestCase):

    def test_added_removed_1_node(self):
        parser = BatmanParser(old=iulinet, new=iulinet2)
        result = parser.diff()
        self.assertTrue(type(result) is dict)
        self.assertTrue(type(result['added']) is list)
        self.assertTrue(type(result['removed']) is list)
        # ensure there are no differences
        self.assertEqual(len(result['added']), 1)
        self.assertEqual(len(result['removed']), 1)
        self.assertEqual(result['added'][0], ('a0:f3:c1:96:94:10', '90:f6:52:f2:8c:2c'))
        self.assertEqual(result['removed'][0], ('a0:f3:c1:96:94:06', '90:f6:52:f2:8c:2c'))

    def test_no_changes(self):
        parser = BatmanParser(old=iulinet, new=iulinet)
        result = parser.diff()
        self.assertTrue(type(result) is dict)
        self.assertTrue(type(result['added']) is list)
        self.assertTrue(type(result['removed']) is list)
        # ensure there are no differences
        self.assertEqual(len(result['added']), 0)
        self.assertEqual(len(result['removed']), 0)
