import os
import unittest
import json
from netdiff.olsr1 import Olsr1Parser


__all__ = ['TestOlsr1Parser']


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
topology1 = open('{0}/topology1.json'.format(CURRENT_DIR)).read()


class TestOlsr1Parser(unittest.TestCase):

    def test_no_changes(self):
        parser = Olsr1Parser(old=topology1, new=topology1)
        result = parser.diff()
        self.assertTrue(type(result) is dict)
        self.assertTrue(type(result['added']) is list)
        self.assertTrue(type(result['removed']) is list)
        # ensure there are no differences
        self.assertEqual(len(result['added']), 0)
        self.assertEqual(len(result['removed']), 0)

    def test_diff_json(self):
        parser = Olsr1Parser(old=topology1, new=topology1)
        result = parser.diff_json(sort_keys=True, indent=4)
        # ensure str
        self.assertTrue(type(result) is str)
        # ensure is json decodable
        self.assertTrue(type(json.loads(result)) is dict)
