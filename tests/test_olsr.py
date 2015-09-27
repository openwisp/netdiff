import os
import six
import networkx

from netdiff import OlsrParser
from netdiff import diff
from netdiff.exceptions import ParserError
from netdiff.tests import TestCase


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
links2 = '{0}/static/olsr-2-links.json'.format(CURRENT_DIR)
links2_cost = '{0}/static/olsr-2-links-cost-changed.json'.format(CURRENT_DIR)
links3 = '{0}/static/olsr-3-links.json'.format(CURRENT_DIR)
links5 = '{0}/static/olsr-5-links.json'.format(CURRENT_DIR)
links5_cost = '{0}/static/olsr-5-links-cost-changed.json'.format(CURRENT_DIR)


class TestOlsrParser(TestCase):

    def test_parse(self):
        p = OlsrParser(links2)
        self.assertIsInstance(p.graph, networkx.Graph)
        # test additional properties in networkx graph
        properties = p.graph.edges(data=True)[0][2]
        self.assertIsInstance(properties['weight'], float)
        self.assertIsInstance(properties['link_quality'], float)
        self.assertIsInstance(properties['neighbor_link_quality'], float)
        # test additional node properties
        properties = p.graph.nodes(data=True)[0][1]
        self.assertIsInstance(properties['local_addresses'], list)

    def test_init(self):
        p = OlsrParser(links3, version='0.6.3', metric='ETC')
        self.assertEqual(p.version, '0.6.3')
        self.assertEqual(p.metric, 'ETC')
        self.assertEqual(p.revision, None)
        p = OlsrParser(links3, version='0.6.3', revision='a', metric='ETC')
        self.assertEqual(p.revision, 'a')

    def test_parse_exception(self):
        with self.assertRaises(ParserError):
            OlsrParser('{ "test": "test" }')

    def test_parse_exception2(self):
        with self.assertRaises(ParserError):
            OlsrParser('{ "topology": [{ "a": "a" }], "mid": [] }')

    def test_parse_exception_mid(self):
        with self.assertRaises(ParserError):
            OlsrParser('{ "topology": [], "missing_mid": [] }')

    def test_json_dict(self):
        p = OlsrParser(links2)
        data = p.json(dict=True)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['type'], 'NetworkGraph')
        self.assertEqual(data['protocol'], 'OLSR')
        self.assertEqual(data['version'], '0.6.6')
        self.assertEqual(data['revision'], '5031a799fcbe17f61d57e387bc3806de')
        self.assertEqual(data['metric'], 'ETX')
        self.assertIsInstance(data['nodes'], list)
        self.assertIsInstance(data['links'], list)
        self.assertEqual(len(data['nodes']), 3)
        self.assertEqual(len(data['links']), 2)
        self.assertIsInstance(data['links'][0]['cost'], float)
        # test additional link properties
        properties = data['links'][0]['properties']
        self.assertIsInstance(properties['link_quality'], float)
        self.assertIsInstance(properties['neighbor_link_quality'], float)
        # test local_addresses
        self.assertIsInstance(data['nodes'][0]['local_addresses'], list)
        found = False
        for node in data['nodes']:
            if node['id'] == '10.150.0.2':
                self.assertEqual(len(node['local_addresses']), 2)
                self.assertEqual(node['local_addresses'][0], '172.16.192.2')
                self.assertEqual(node['local_addresses'][1], '192.168.0.2')
                found = True
        self.assertTrue(found)

    def test_json_string(self):
        p = OlsrParser(links2)
        data = p.json()
        self.assertIsInstance(data, six.string_types)
        self.assertIn('NetworkGraph', data)
        self.assertIn('protocol', data)
        self.assertIn('version', data)
        self.assertIn('revision', data)
        self.assertIn('metric', data)
        self.assertIn('OLSR', data)
        self.assertIn('0.6.6', data)
        self.assertIn('5031a799fcbe17f61d57e387bc3806de', data)
        self.assertIn('ETX', data)
        self.assertIn('links', data)
        self.assertIn('nodes', data)

    def test_no_changes(self):
        old = OlsrParser(links2)
        new = OlsrParser(links2)
        result = diff(old, new)
        self.assertIsInstance(result, dict)
        self.assertIsNone(result['added'])
        self.assertIsNone(result['removed'])
        self.assertIsNone(result['changed'])

    def test_added_1_link(self):
        old = OlsrParser(links2)
        new = OlsrParser(links3)
        result = diff(old, new)
        self.assertIsNone(result['removed'])
        self.assertIsNone(result['changed'])
        # ensure there are differences
        self.assertEqual(len(result['added']['links']), 1)
        self.assertEqual(len(result['added']['nodes']), 1)
        # ensure correct link added
        self.assertIn('10.150.0.5', result['added']['links'][0].values())
        self.assertIn('10.150.0.4', result['added']['links'][0].values())
        # ensure correct node added
        self.assertIn('10.150.0.5', result['added']['nodes'][0].values())

    def test_added_1_link_sub(self):
        old = OlsrParser(links2)
        new = OlsrParser(links3)
        result = new - old
        self.assertIsNone(result['removed'])
        self.assertIsNone(result['changed'])
        # ensure there are differences
        self.assertEqual(len(result['added']['links']), 1)
        self.assertEqual(len(result['added']['nodes']), 1)
        # ensure correct link added
        self.assertIn('10.150.0.5', result['added']['links'][0].values())
        self.assertIn('10.150.0.4', result['added']['links'][0].values())
        # ensure correct node added
        self.assertIn('10.150.0.5', result['added']['nodes'][0].values())

    def test_removed_1_link(self):
        old = OlsrParser(links3)
        new = OlsrParser(links2)
        result = diff(old, new)
        self.assertIsNone(result['added'])
        self.assertIsNone(result['changed'])
        self.assertIsInstance(result, dict)
        self.assertTrue(type(result['removed']['links']) is list)
        # ensure there are differences
        self.assertEqual(len(result['removed']['links']), 1)
        self.assertEqual(len(result['removed']['nodes']), 1)
        # ensure correct link removed
        self.assertIn('10.150.0.5', result['removed']['links'][0].values())
        self.assertIn('10.150.0.4', result['removed']['links'][0].values())
        # ensure correct node removed
        self.assertIn('10.150.0.5', result['removed']['nodes'][0].values())

    def test_simple_diff(self):
        old = OlsrParser(links3)
        new = OlsrParser(links5)
        result = diff(old, new)
        self.assertIsNone(result['changed'])
        # ensure there are differences
        self.assertEqual(len(result['added']['links']), 3)
        self.assertEqual(len(result['removed']['links']), 1)
        self.assertEqual(len(result['added']['nodes']), 2)
        self.assertEqual(len(result['removed']['nodes']), 1)
        # ensure 3 links added
        self._test_expected_links(
            graph=result['added'],
            expected_links=[
                ('10.150.0.3', '10.150.0.7'),
                ('10.150.0.3', '10.150.0.6'),
                ('10.150.0.7', '10.150.0.6'),
            ]
        )
        self._test_expected_links(
            graph=result['removed'],
            expected_links=[('10.150.0.5', '10.150.0.4')]
        )
        added_nodes = [node['id'] for node in result['added']['nodes']]
        self.assertIn('10.150.0.6', added_nodes)
        self.assertIn('10.150.0.7', added_nodes)
        self.assertIn('10.150.0.5', result['removed']['nodes'][0].values())

    def test_cost(self):
        parser = OlsrParser(links2)
        graph = parser.json(dict=True)
        a = graph['links'][0]['cost']
        b = graph['links'][1]['cost']
        self.assertIn(27.669921875, [a, b])
        self.assertIn(1.0, [a, b])

    def test_diff_format(self):
        old = OlsrParser(links3)
        new = OlsrParser(links5)
        result = diff(old, new)
        data = result['added']
        self.assertEqual(data['type'], 'NetworkGraph')
        self.assertEqual(data['protocol'], 'OLSR')
        self.assertEqual(data['version'], '0.6.6')
        self.assertEqual(data['revision'], '5031a799fcbe17f61d57e387bc3806de')
        self.assertEqual(data['metric'], 'ETX')
        self.assertIsInstance(data['nodes'], list)
        self.assertIsInstance(data['links'], list)
        data = result['removed']
        self.assertEqual(data['type'], 'NetworkGraph')
        self.assertEqual(data['protocol'], 'OLSR')
        self.assertEqual(data['version'], '0.6.6')
        self.assertEqual(data['revision'], '5031a799fcbe17f61d57e387bc3806de')
        self.assertEqual(data['metric'], 'ETX')
        self.assertIsInstance(data['nodes'], list)
        self.assertIsInstance(data['links'], list)

    def test_cost_changes_1(self):
        old = OlsrParser(links2)
        new = OlsrParser(links2_cost)
        result = diff(old, new)
        self.assertIsNone(result['added'])
        self.assertIsNone(result['removed'])
        self.assertIsInstance(result['changed'], dict)
        self.assertEqual(len(result['changed']['nodes']), 0)
        links = result['changed']['links']
        self.assertTrue(type(links) is list)
        self.assertEqual(len(links), 2)
        # ensure results are correct
        self.assertTrue(1.302734375 in (links[0]['cost'], links[1]['cost']))
        self.assertTrue(1.0234375 in (links[0]['cost'], links[1]['cost']))

    def test_cost_changes_2(self):
        old = OlsrParser(links5)
        new = OlsrParser(links5_cost)
        result = diff(old, new)
        self.assertIsNone(result['added'])
        self.assertIsNone(result['removed'])
        self.assertIsInstance(result['changed'], dict)
        self.assertEqual(len(result['changed']['nodes']), 0)
        links = result['changed']['links']
        self.assertEqual(len(links), 4)
        costs = [link['cost'] for link in links]
        self.assertIn(1.0, costs)
        self.assertIn(2.0, costs)
        self.assertIn(1.50390625, costs)
        self.assertIn(3.515625, costs)

    def test_link_with_infinite_cost(self):
        p = OlsrParser({
            "topology": [
                {
                    "lastHopIP": "10.150.0.2",
                    "destinationIP": "10.150.0.3",
                    "linkQuality": 0.195,
                    "neighborLinkQuality": 0.184,
                    "tcEdgeCost": float('inf'),
                    "validityTime": 284572
                }
            ],
            "mid": []
        })
        # ensure link is ignored
        self.assertEqual(len(p.graph.edges()), 0)
