import os
import six
import networkx

from netdiff import BatmanParser
from netdiff import diff
from netdiff.tests import TestCase
from netdiff.exceptions import ParserError


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
iulinet = open('{0}/static/batman.json'.format(CURRENT_DIR)).read()
iulinet2 = open('{0}/static/batman-1+1.json'.format(CURRENT_DIR)).read()
duplicated = open('{0}/static/batman-duplicated.json'.format(CURRENT_DIR)).read()


class TestBatmanParser(TestCase):

    def test_parse(self):
        p = BatmanParser(iulinet)
        self.assertIsInstance(p.graph, networkx.Graph)
        properties = p.graph.edges(data=True)[0][2]
        self.assertIsInstance(properties['weight'], float)
        # test additional properties in nodes of networkx graph
        properties = p.graph.nodes(data=True)[0][1]
        self.assertIsInstance(properties['local_addresses'], list)
        self.assertIsInstance(properties['clients'], list)

    def test_parse_exception(self):
        with self.assertRaises(ParserError):
            BatmanParser('{ "test": "test" }')

    def test_parse_exception2(self):
        with self.assertRaises(ParserError):
            BatmanParser('{ "topology": [{ "a": "a" }] }')

    def test_json_dict(self):
        p = BatmanParser(iulinet)
        data = p.json(dict=True)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['type'], 'NetworkGraph')
        self.assertEqual(data['protocol'], 'batman-adv')
        self.assertEqual(data['version'], '2014.3.0')
        self.assertEqual(data['metric'], 'TQ')
        self.assertIsInstance(data['nodes'], list)
        self.assertIsInstance(data['links'], list)
        self.assertEqual(len(data['nodes']), 5)
        self.assertEqual(len(data['links']), 4)
        self.assertIsInstance(data['links'][0]['cost'], float)
        # ensure additional node properties are present
        found = False
        for node in data['nodes']:
            if node['id'] == '90:f6:52:f2:8c:2c':
                self.assertIsInstance(node['local_addresses'], list)
                self.assertIsInstance(node['properties']['clients'], list)
                found = True
                break
        self.assertTrue(found)
        found = False
        # ensure local_addresses not present if empty
        for node in data['nodes']:
            if node['id'] == 'a0:f3:c1:96:94:06':
                self.assertFalse('local_addresses' in node)
                found = True
                break
        self.assertTrue(found)

    def test_json_string(self):
        p = BatmanParser(iulinet)
        data = p.json()
        self.assertIsInstance(data, six.string_types)
        self.assertIn('NetworkGraph', data)
        self.assertIn('protocol', data)
        self.assertIn('version', data)
        self.assertIn('metric', data)
        self.assertIn('batman-adv', data)
        self.assertIn('2014.3.0', data)
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

    def test_no_changes(self):
        old = BatmanParser(iulinet)
        new = BatmanParser(iulinet)
        result = diff(old, new)
        self.assertIsInstance(result, dict)
        self.assertIsNone(result['added'])
        self.assertIsNone(result['removed'])

    def test_duplicated(self):
        nodup = BatmanParser(iulinet)
        dup = BatmanParser(duplicated)
        # nodup and dup have the same amount of nodes and edges
        self.assertEqual(len(nodup.graph.edges()), len(dup.graph.edges()))
        self.assertEqual(len(nodup.graph.nodes()), len(dup.graph.nodes()))

    def test_get_primary_address_ValueError(self):
        p = BatmanParser(iulinet)
        with self.assertRaises(ValueError):
            p._get_primary_address('wrong', [['aa:bb:cc:dd:ee:ff']])
