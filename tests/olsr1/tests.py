import os
import unittest
import json
from netdiff.olsr1 import Olsr1Parser


__all__ = ['TestOlsr1Parser']


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
links2 = open('{0}/2links.json'.format(CURRENT_DIR)).read()
links3 = open('{0}/3links.json'.format(CURRENT_DIR)).read()
links5 = open('{0}/5links.json'.format(CURRENT_DIR)).read()


class TestOlsr1Parser(unittest.TestCase):

    def test_no_changes(self):
        parser = Olsr1Parser(old=links2, new=links2)
        result = parser.diff()
        self.assertTrue(type(result) is dict)
        self.assertTrue(type(result['added']) is list)
        self.assertTrue(type(result['removed']) is list)
        # ensure there are no differences
        self.assertEqual(len(result['added']), 0)
        self.assertEqual(len(result['removed']), 0)

    def test_diff_json(self):
        parser = Olsr1Parser(old=links3, new=links3)
        result = parser.diff_json(sort_keys=True, indent=4)
        # ensure str
        self.assertTrue(type(result) is str)
        # ensure is json decodable
        self.assertTrue(type(json.loads(result)) is dict)

    def test_added_1_link(self):
        parser = Olsr1Parser(old=links2, new=links3)
        result = parser.diff()
        # ensure there are no differences
        self.assertEqual(len(result['added']), 1)
        self.assertEqual(len(result['removed']), 0)
        # ensure 1 link added
        self.assertEqual(result['added'][0], ('10.150.0.5', '10.150.0.4'))

    def test_removed_1_link(self):
        parser = Olsr1Parser(old=links3, new=links2)
        result = parser.diff()
        self.assertTrue(type(result) is dict)
        self.assertTrue(type(result['added']) is list)
        self.assertTrue(type(result['removed']) is list)
        # ensure there are no differences
        self.assertEqual(len(result['added']), 0)
        self.assertEqual(len(result['removed']), 1)
        # ensure 1 link removed
        self.assertEqual(result['removed'][0], ('10.150.0.5', '10.150.0.4'))

    def test_simple_diff(self):
        parser = Olsr1Parser(old=links3, new=links5)
        result = parser.diff()
        # ensure there are no differences
        self.assertEqual(len(result['added']), 3)
        self.assertEqual(len(result['removed']), 1)
        # ensure 3 links added
        self.assertEqual(result['added'], [
            ('10.150.0.3', '10.150.0.7'),
            ('10.150.0.3', '10.150.0.6'),
            ('10.150.0.7', '10.150.0.6'),
        ])
        self.assertEqual(result['removed'], [
            ('10.150.0.5', '10.150.0.4'),
        ])
