import os

import networkx

from netdiff import OlsrParser, diff
from netdiff.exceptions import ParserError
from netdiff.tests import TestCase

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
links2 = open('{0}/static/olsr-2-links.txt'.format(CURRENT_DIR)).read()
links2_cost = open(
    '{0}/static/olsr-2-links-cost-changed.txt'.format(CURRENT_DIR)
).read()
links3 = open('{0}/static/olsr-3-links.txt'.format(CURRENT_DIR)).read()
links5 = open('{0}/static/olsr-5-links.txt'.format(CURRENT_DIR)).read()


class TestOlsrTxtinfoParser(TestCase):
    def test_parse(self):
        p = OlsrParser(links2)
        self.assertIsInstance(p.graph, networkx.Graph)
        # test additional properties in networkx graph
        properties = list(p.graph.edges(data=True))[0][2]
        self.assertIsInstance(properties['weight'], float)
        self.assertIsInstance(properties['link_quality'], float)
        self.assertIsInstance(properties['neighbor_link_quality'], float)
        # test additional node properties
        properties = list(p.graph.nodes(data=True))[0][1]
        self.assertIsInstance(properties['local_addresses'], list)

    def test_parse_exception_topology(self):
        with self.assertRaises(ParserError):
            OlsrParser('clearly wrong')
        with self.assertRaises(ParserError):
            OlsrParser('Table: Topology\n......')

    def test_parse_exception_mid(self):
        with self.assertRaises(ParserError):
            OlsrParser('Table: Topology\n\n\nMISSING MID')

    def test_json_dict(self):
        p = OlsrParser(links2)
        data = p.json(dict=True)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['type'], 'NetworkGraph')
        self.assertEqual(data['protocol'], 'OLSR')
        self.assertEqual(data['version'], '0.8')
        self.assertEqual(data['revision'], None)
        self.assertEqual(data['metric'], 'ETX')
        self.assertIsInstance(data['nodes'], list)
        self.assertIsInstance(data['links'], list)
        self.assertEqual(len(data['nodes']), 3)
        self.assertEqual(len(data['links']), 2)
        self.assertIsInstance(data['links'][0]['cost'], float)
        # test additional properties
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
        self.assertIsInstance(data, str)
        self.assertIn('NetworkGraph', data)
        self.assertIn('protocol', data)
        self.assertIn('version', data)
        self.assertIn('revision', data)
        self.assertIn('metric', data)
        self.assertIn('OLSR', data)
        self.assertIn('0.8', data)
        self.assertIn('null', data)
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
        self.assertEqual(result['changed']['links'], [])
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
        self.assertEqual(result['changed']['links'], [])
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
        self.assertEqual(result['changed']['links'], [])
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

    def test_changed_3_nodes(self):
        old = OlsrParser(links2)
        new = OlsrParser(links2_cost)
        result = diff(old, new)
        self.assertIsInstance(result['changed'], dict)
        self.assertEqual(len(result['changed']['nodes']), 3)
        node = result['changed']['nodes'][0]
        self.assertEqual(node['id'], '10.150.0.2')
        self.assertEqual(node['label'], '')
        self.assertEqual(node['local_addresses'], [])
        self.assertEqual(node['properties'], {})
        node = result['changed']['nodes'][1]
        self.assertEqual(node['id'], '10.150.0.3')
        self.assertEqual(node['label'], '')
        self.assertEqual(node['local_addresses'], [])
        self.assertEqual(node['properties'], {})
        node = result['changed']['nodes'][2]
        self.assertEqual(node['id'], '10.150.0.4')
        self.assertEqual(node['label'], '')
        self.assertEqual(node['local_addresses'], [])
        self.assertEqual(node['properties'], {})

    def test_simple_diff(self):
        old = OlsrParser(links3)
        new = OlsrParser(links5)
        result = diff(old, new)
        self.assertEqual(result['changed']['nodes'], [])
        self.assertEqual(len(result['changed']['links']), 1)
        link = result['changed']['links'][0]
        self.assertEqual(link['source'], '10.150.0.3')
        self.assertEqual(link['target'], '10.150.0.2')
        self.assertEqual(link['cost'], 27.669)
        self.assertEqual(link['cost_text'], '')
        self.assertEqual(
            link['properties'], {'neighbor_link_quality': 0.184, 'link_quality': 0.195}
        )
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
            ],
        )
        self._test_expected_links(
            graph=result['removed'], expected_links=[('10.150.0.5', '10.150.0.4')]
        )
        added_nodes = [node['id'] for node in result['added']['nodes']]
        self.assertIn('10.150.0.6', added_nodes)
        self.assertIn('10.150.0.7', added_nodes)
        self.assertIn('10.150.0.5', result['removed']['nodes'][0].values())

    def test_cost(self):
        parser = OlsrParser(links2)
        graph = parser.json(dict=True)
        self.assertEqual(27.669, graph['links'][0]['cost'])
        self.assertEqual(1.0, graph['links'][1]['cost'])

    def test_diff_format(self):
        old = OlsrParser(links3)
        new = OlsrParser(links5)
        result = diff(old, new)
        data = result['added']
        self.assertEqual(data['type'], 'NetworkGraph')
        self.assertEqual(data['protocol'], 'OLSR')
        self.assertEqual(data['version'], '0.8')
        self.assertEqual(data['revision'], None)
        self.assertEqual(data['metric'], 'ETX')
        self.assertIsInstance(data['nodes'], list)
        self.assertIsInstance(data['links'], list)
        data = result['removed']
        self.assertEqual(data['type'], 'NetworkGraph')
        self.assertEqual(data['protocol'], 'OLSR')
        self.assertEqual(data['version'], '0.8')
        self.assertEqual(data['revision'], None)
        self.assertEqual(data['metric'], 'ETX')
        self.assertIsInstance(data['nodes'], list)
        self.assertIsInstance(data['links'], list)
        data = result['changed']
        self.assertEqual(data['type'], 'NetworkGraph')
        self.assertEqual(data['protocol'], 'OLSR')
        self.assertEqual(data['version'], '0.8')
        self.assertEqual(data['revision'], None)
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
        self.assertEqual(len(result['changed']['nodes']), 3)
        self.assertIsInstance(result['changed']['links'], list)
        self.assertEqual(len(result['changed']['links']), 2)
        links = result['changed']['links']
        # ensure results are correct
        self.assertTrue(links[0]['cost'], 1.302)
        self.assertTrue(links[1]['cost'], 1.023)

    def test_link_with_infinite_cost(self):
        data = """Table: Topology
Dest. IP\tLast hop IP\tLQ\tNLQ\tCost
10.150.0.3\t10.150.0.2\t0.195\t0.184\tINFINITE

Table: MID
IP address\tAliases

"""
        p = OlsrParser(data)
        # ensure link is ignored
        self.assertEqual(len(p.graph.edges()), 0)
