import os
import six
import networkx

from netdiff import CnmlParser
from netdiff import diff
from netdiff.exceptions import NetParserException
from netdiff.tests import TestCase


__all__ = ['TestCnmlParser']


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
cnml1 = '{0}/../static/26494_detail_1.cnml'.format(CURRENT_DIR)
cnml2 = '{0}/../static/26494_detail_2.cnml'.format(CURRENT_DIR)
cnml3 = '{0}/../static/26494_detail_3.cnml'.format(CURRENT_DIR)


class TestCnmlParser(TestCase):

    def test_parse(self):
        p = CnmlParser(cnml1)
        self.assertIsInstance(p.graph, networkx.Graph)

    def test_parse_exception(self):
        with self.assertRaises(NetParserException):
            CnmlParser('{ "test": "test" }')

    def test_parse_exception2(self):
        with self.assertRaises(NetParserException):
            CnmlParser('telnet://127.0.0.1:9090')

    def test_json_dict(self):
        p = CnmlParser(cnml1)
        data = p.json(dict=True)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['type'], 'NetworkGraph')
        self.assertEqual(data['protocol'], 'static')
        self.assertEqual(data['version'], '0.1')
        self.assertEqual(data['revision'], None)
        self.assertEqual(data['metric'], None)
        self.assertIsInstance(data['nodes'], list)
        self.assertIsInstance(data['links'], list)
        self.assertEqual(len(data['nodes']), 5)
        self.assertEqual(len(data['links']), 3)

    def test_json_string(self):
        p = CnmlParser(cnml1)
        data = p.json()
        self.assertIsInstance(data, six.string_types)
        self.assertIn('NetworkGraph', data)
        self.assertIn('protocol', data)
        self.assertIn('version', data)
        self.assertIn('revision', data)
        self.assertIn('metric', data)
        self.assertIn('0.1', data)
        self.assertIn('links', data)
        self.assertIn('nodes', data)

    def test_no_changes(self):
        old = CnmlParser(cnml1)
        new = CnmlParser(cnml1)
        result = diff(old, new)
        self.assertTrue(type(result) is dict)
        self.assertTrue(type(result['added']) is list)
        self.assertTrue(type(result['removed']) is list)
        # ensure there are no differences
        self.assertEqual(len(result['added']), 0)
        self.assertEqual(len(result['removed']), 0)

    def test_added_1_link(self):
        old = CnmlParser(cnml1)
        new = CnmlParser(cnml2)
        result = diff(old, new)
        # ensure there are differences
        self.assertEqual(len(result['added']), 1)
        self.assertEqual(len(result['removed']), 0)
        # ensure 1 link added
        self.assertIn('10.228.172.97', result['added'][0])
        self.assertIn('10.228.172.101', result['added'][0])

    def test_removed_1_link(self):
        old = CnmlParser(cnml2)
        new = CnmlParser(cnml1)
        result = diff(old, new)
        self.assertTrue(type(result) is dict)
        self.assertTrue(type(result['added']) is list)
        self.assertTrue(type(result['removed']) is list)
        # ensure there are differences
        self.assertEqual(len(result['added']), 0)
        self.assertEqual(len(result['removed']), 1)
        # ensure 1 link removed
        self.assertIn('10.228.172.97', result['removed'][0])
        self.assertIn('10.228.172.101', result['removed'][0])

    def test_simple_diff(self):
        old = CnmlParser(cnml1)
        new = CnmlParser(cnml3)
        result = diff(old, new)
        # ensure there are differences
        self.assertEqual(len(result['added']), 2)
        self.assertEqual(len(result['removed']), 2)
        # ensure 2 links added
        self._test_expected_links(
            links=result['added'],
            expected_links=[
                ('10.228.172.97', '10.228.172.101'),
                ('10.228.172.194', '10.228.172.193'),
            ]
        )
        # ensure 2 links removed
        self._test_expected_links(
            links=result['removed'],
            expected_links=[
                ('10.228.172.33', '10.228.172.34'),
                ('10.228.172.33', '10.228.172.36'),
            ]
        )
