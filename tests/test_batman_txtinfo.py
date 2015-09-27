import os
import six
import networkx

from netdiff import BatmanParser
from netdiff import diff
from netdiff.tests import TestCase
from netdiff.exceptions import ParserError


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
iulinet = open('{0}/static/batman.txt'.format(CURRENT_DIR)).read()
iulinet2 = open('{0}/static/batman-1+1.txt'.format(CURRENT_DIR)).read()


class TestBatmanTxtinfoParser(TestCase):

    def test_parse(self):
        p = BatmanParser(iulinet)
        self.assertIsInstance(p.graph, networkx.Graph)
        self.assertEqual(len(p.graph.nodes()), 5)
        self.assertEqual(len(p.graph.edges()), 4)
        properties = p.graph.edges(data=True)[0][2]
        self.assertIsInstance(properties['weight'], float)

    def test_parse_exception(self):
        with self.assertRaises(ParserError):
            BatmanParser('WRONG')

    def test_json_dict(self):
        p = BatmanParser(iulinet)
        data = p.json(dict=True)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['type'], 'NetworkGraph')
        self.assertEqual(data['protocol'], 'batman-adv')
        self.assertEqual(data['version'], '2015.0')
        self.assertEqual(data['metric'], 'TQ')
        self.assertIsInstance(data['nodes'], list)
        self.assertIsInstance(data['links'], list)
        self.assertEqual(len(data['nodes']), 5)
        self.assertEqual(len(data['links']), 4)
        self.assertIsInstance(data['links'][0]['cost'], float)

    def test_json_string(self):
        p = BatmanParser(iulinet)
        data = p.json()
        self.assertIsInstance(data, six.string_types)
        self.assertIn('NetworkGraph', data)
        self.assertIn('protocol', data)
        self.assertIn('version', data)
        self.assertIn('metric', data)
        self.assertIn('batman-adv', data)
        self.assertIn('2015.0', data)
        self.assertIn('TQ', data)
        self.assertIn('links', data)
        self.assertIn('nodes', data)

    def test_added_removed_1_node(self):
        old = BatmanParser(iulinet)
        new = BatmanParser(iulinet2)
        result = diff(old, new)
        self.assertIsInstance(result, dict)
        self.assertTrue(type(result['added']['links']) is list)
        self.assertTrue(type(result['removed']['links']) is list)
        # ensure there are no differences
        self.assertEqual(len(result['added']['links']), 1)
        self.assertEqual(len(result['removed']['links']), 1)
        self._test_expected_links(
            graph=result['added'],
            expected_links=[
                ('a0:f3:c1:96:94:10', '90:f6:52:f2:8c:2c')
            ]
        )
        self._test_expected_links(
            graph=result['removed'],
            expected_links=[
                ('a0:f3:c1:96:94:06', '90:f6:52:f2:8c:2c')
            ]
        )
        self.assertIsNone(result['changed'])

    def test_no_changes(self):
        old = BatmanParser(iulinet)
        new = BatmanParser(iulinet)
        result = diff(old, new)
        self.assertIsInstance(result, dict)
        self.assertIsNone(result['added'])
        self.assertIsNone(result['removed'])
        self.assertIsNone(result['changed'])
