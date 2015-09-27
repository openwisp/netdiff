import os
import six
import networkx

from netdiff import Bmx6Parser
from netdiff import diff
from netdiff.tests import TestCase
from netdiff.exceptions import ParserError


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
topo = open('{0}/static/bmx6.json'.format(CURRENT_DIR)).read()
topo2 = open('{0}/static/bmx6-1+1.json'.format(CURRENT_DIR)).read()


class TestBmx6Parser(TestCase):

    def test_parse(self):
        p = Bmx6Parser(topo)
        self.assertIsInstance(p.graph, networkx.Graph)
        # test additional properties in networkx graph
        properties = p.graph.edges(data=True)[0][2]
        self.assertIsInstance(properties['weight'], float)
        self.assertIsInstance(properties['tx_rate'], int)
        self.assertIsInstance(properties['rx_rate'], int)

    def test_parse_exception(self):
        with self.assertRaises(ParserError):
            Bmx6Parser('[{ "test": "test" }]')

    def test_json_dict(self):
        p = Bmx6Parser(topo)
        data = p.json(dict=True)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['type'], 'NetworkGraph')
        self.assertEqual(data['protocol'], 'BMX6_b6m')
        self.assertEqual(data['version'], '0')
        self.assertEqual(data['metric'], 'none')
        self.assertIsInstance(data['nodes'], list)
        self.assertIsInstance(data['links'], list)
        self.assertEqual(len(data['nodes']), 7)
        self.assertEqual(len(data['links']), 6)
        self.assertIsInstance(data['links'][0]['cost'], float)
        self.assertGreater(data['links'][0]['cost'], 1)
        # test additional properties
        properties = data['links'][0]['properties']
        self.assertIsInstance(properties['tx_rate'], int)
        self.assertIsInstance(properties['rx_rate'], int)

    def test_json_string(self):
        p = Bmx6Parser(topo)
        data = p.json()
        self.assertIsInstance(data, six.string_types)
        self.assertIn('NetworkGraph', data)
        self.assertIn('protocol', data)
        self.assertIn('version', data)
        self.assertIn('metric', data)
        self.assertIn('BMX6_b6m', data)
        self.assertIn('0', data)
        self.assertIn('none', data)
        self.assertIn('links', data)
        self.assertIn('nodes', data)

    def test_added_removed_1_node(self):
        old = Bmx6Parser(topo)
        new = Bmx6Parser(topo2)
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
                ('P9SFCiutatGranada73-68f5', 'P9SFDrTruetaa183-b715')
            ]
        )
        self._test_expected_links(
            graph=result['removed'],
            expected_links=[
                ('P9SFCiutatGranada73-68f5', 'P9SFDrTruetaa183-b713')
            ]
        )

    def test_no_changes(self):
        old = Bmx6Parser(topo)
        new = Bmx6Parser(topo)
        result = diff(old, new)
        self.assertIsInstance(result, dict)
        self.assertIsNone(result['added'])
        self.assertIsNone(result['removed'])
