import os

import networkx

from netdiff import NetJsonParser, diff
from netdiff.exceptions import ParserError
from netdiff.tests import TestCase

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
links2 = open('{0}/static/netjson-2-links.json'.format(CURRENT_DIR)).read()
links3 = open('{0}/static/netjson-3-links.json'.format(CURRENT_DIR)).read()
nodes1 = open('{0}/static/netjson-nodes-1.json'.format(CURRENT_DIR)).read()
nodes2 = open('{0}/static/netjson-nodes-2.json'.format(CURRENT_DIR)).read()


class TestNetJsonParser(TestCase):
    def test_parse(self):
        p = NetJsonParser(links2)
        self.assertIsInstance(p.graph, networkx.Graph)
        self.assertEqual(p.version, '0.6.6')
        self.assertEqual(p.revision, '5031a799fcbe17f61d57e387bc3806de')
        self.assertEqual(p.metric, 'ETX')
        # test additional properties in links of network graph
        properties = list(p.graph.edges(data=True))[0][2]
        self.assertIsInstance(properties['custom_property'], bool)
        # test additional properties in nodes of networkx graph
        properties = list(p.graph.nodes(data=True))[0][1]
        self.assertIsInstance(properties['local_addresses'], list)
        self.assertIsInstance(properties['hostname'], str)

    def test_parse_directed(self):
        p = NetJsonParser(links2, directed=True)
        self.assertIsInstance(p.graph, networkx.DiGraph)
        self.assertEqual(p.version, '0.6.6')
        self.assertEqual(p.revision, '5031a799fcbe17f61d57e387bc3806de')
        self.assertEqual(p.metric, 'ETX')
        # test additional properties in links of network graph
        properties = list(p.graph.edges(data=True))[0][2]
        self.assertIsInstance(properties['custom_property'], bool)
        # test additional properties in nodes of networkx graph
        properties = list(p.graph.nodes(data=True))[0][1]
        self.assertIsInstance(properties['local_addresses'], list)
        self.assertIsInstance(properties['hostname'], str)

    def test_parse_string_graph(self):
        data = """{
    "type": "NetworkGraph",
    "protocol": "OLSR",
    "version": "0.6.6",
    "revision": "5031a799fcbe17f61d57e387bc3806de",
    "metric": "ETX",
    "nodes": [
        {
            "id": "10.150.0.3"
        },
        {
            "id": "10.150.0.2"
        }
    ],
    "links": [
        {
            "source": "10.150.0.3",
            "target": "10.150.0.2",
            "cost": 1.0
        }
    ]
}"""
        p = NetJsonParser(data)
        self.assertEqual(len(p.graph.nodes()), 2)
        self.assertIn('10.150.0.3', p.graph.nodes())
        self.assertIn('10.150.0.2', p.graph.nodes())
        self.assertEqual(len(p.graph.edges()), 1)
        self.assertEqual(list(p.graph.edges(data=True))[0][2]['weight'], 1.0)

    def test_parse_one_way_directed_string_graph(self):
        """
        In directed mode, it should be possible to have an edge in only one direction
        """
        data = """{
    "type": "NetworkGraph",
    "protocol": "OLSR",
    "version": "0.6.6",
    "revision": "5031a799fcbe17f61d57e387bc3806de",
    "metric": "ETX",
    "nodes": [
        {
            "id": "10.150.0.3"
        },
        {
            "id": "10.150.0.2"
        }
    ],
    "links": [
        {
            "source": "10.150.0.3",
            "target": "10.150.0.2",
            "cost": 1.0
        }
    ]
}"""
        p = NetJsonParser(data, directed=True)
        self.assertEqual(len(p.graph.nodes()), 2)
        self.assertIn('10.150.0.3', p.graph.nodes())
        self.assertIn('10.150.0.2', p.graph.nodes())
        self.assertEqual(len(p.graph.edges()), 1)
        self.assertEqual(
            len(p.graph.adj["10.150.0.3"]), 1, msg="10.150.0.3 should have an edge"
        )
        self.assertEqual(
            len(p.graph.adj["10.150.0.2"]), 0, msg="10.150.0.2 should have no edges"
        )
        self.assertEqual(
            p.graph.edges[("10.150.0.3", "10.150.0.2")]['weight'],
            1.0,
            msg="Expected directed edge does not exist!",
        )

    def test_parse_forward_backward_directed_string_graph3(self):
        """
        In directed mode, it should be possible to have a forward edge and a backward edge with different
        weights
        """
        data = """{
    "type": "NetworkGraph",
    "protocol": "OLSR",
    "version": "0.6.6",
    "revision": "5031a799fcbe17f61d57e387bc3806de",
    "metric": "ETX",
    "nodes": [
        {
            "id": "10.150.0.3"
        },
        {
            "id": "10.150.0.2"
        }
    ],
    "links": [
        {
            "source": "10.150.0.3",
            "target": "10.150.0.2",
            "cost": 1.0
        },
        {
            "source": "10.150.0.2",
            "target": "10.150.0.3",
            "cost": 99.0
        }
    ]
}"""
        p = NetJsonParser(data, directed=True)
        self.assertEqual(len(p.graph.nodes()), 2)
        self.assertIn('10.150.0.3', p.graph.nodes())
        self.assertIn('10.150.0.2', p.graph.nodes())
        self.assertEqual(len(p.graph.edges()), 2)
        self.assertEqual(
            p.graph.edges[("10.150.0.3", "10.150.0.2")]['weight'],
            1.0,
            msg="Forward edge weight was incorrectly overwritten!",
        )
        self.assertEqual(
            p.graph.edges[("10.150.0.2", "10.150.0.3")]['weight'],
            99.0,
            msg="Backward edge weight was not correctly assigned!",
        )

    def test_parse_exception(self):
        with self.assertRaises(ParserError):
            NetJsonParser('{ "test": "test" }')

    def test_parse_exception2(self):
        with self.assertRaises(ParserError):
            NetJsonParser(
                {
                    "type": "WRONG",
                    "protocol": "OLSR",
                    "version": "0.6.3",
                    "metric": "ETX",
                }
            )

    def test_parse_exception3(self):
        with self.assertRaises(ParserError):
            NetJsonParser(
                {
                    "type": "NetworkGraph",
                    "protocol": "OLSR",
                    "version": "0.6.3",
                    "metric": "ETX",
                }
            )

    def test_parse_exception4(self):
        with self.assertRaises(ParserError):
            NetJsonParser(
                {
                    "type": "NetworkGraph",
                    "protocol": "OLSR",
                    "version": "0.6.3",
                    "metric": "ETX",
                    "nodes": [
                        {"id": "10.150.0.3"},
                        {"id": "10.150.0.2"},
                        {"id": "10.150.0.4"},
                    ],
                    "links": [{"wrong": "10.150.0.3"}, {"wrong": "10.150.0.3"}],
                }
            )

    def test_json_dict(self):
        p = NetJsonParser(links2)
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
        # ensure additional node properties are present
        self.assertIn('properties', data['nodes'][0])
        self.assertIn('hostname', data['nodes'][0]['properties'])
        # ensure local_addresses is present
        self.assertIn('local_addresses', data['nodes'][0])
        # ensure additional link properties are present
        self.assertIn('properties', data['links'][0])
        self.assertIn('custom_property', data['links'][0]['properties'])
        # check presence of labels, we need to find 2
        labels = []
        for node in data['nodes']:
            if 'label' in node:
                labels.append(node['label'])
        self.assertEqual(len(labels), 3)
        self.assertIn('nodeA', labels)
        self.assertIn('nodeB', labels)
        self.assertIn('', labels)

    def test_json_string(self):
        p = NetJsonParser(links2)
        data = p.json()
        self.assertIsInstance(data, str)
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
        old = NetJsonParser(links2)
        new = NetJsonParser(links2)
        result = diff(old, new)
        self.assertIsInstance(result, dict)
        self.assertIsNone(result['added'])
        self.assertIsNone(result['removed'])

    def test_added_1_link(self):
        old = NetJsonParser(links2)
        new = NetJsonParser(links3)
        result = diff(old, new)
        self.assertIsNone(result['removed'])
        # ensure there are no differences
        self.assertEqual(len(result['added']['links']), 1)
        self.assertEqual(len(result['added']['nodes']), 1)
        # ensure correct link added
        self.assertIn('10.150.0.5', result['added']['links'][0].values())
        self.assertIn('10.150.0.4', result['added']['links'][0].values())
        # ensure correct node added
        self.assertIn('10.150.0.5', result['added']['nodes'][0].values())
        # ensure changed value is correct
        link = result['changed']['links'][1]
        self.assertEqual(link['source'], '10.150.0.3')
        self.assertEqual(link['target'], '10.150.0.4')
        self.assertEqual(link['cost'], 1048)

    def test_removed_1_link(self):
        old = NetJsonParser(links3)
        new = NetJsonParser(links2)
        result = diff(old, new)
        self.assertIsNone(result['added'])
        self.assertIsInstance(result, dict)
        self.assertTrue(type(result['removed']['links']) is list)
        self.assertTrue(type(result['removed']['nodes']) is list)
        # ensure differences
        self.assertEqual(len(result['removed']['links']), 1)
        self.assertEqual(len(result['removed']['nodes']), 1)
        # ensure 1 link removed
        self.assertIn('10.150.0.5', result['removed']['links'][0].values())
        self.assertIn('10.150.0.4', result['removed']['links'][0].values())
        # ensure correct node added
        self.assertIn('10.150.0.5', result['removed']['nodes'][0].values())

    def test_added_1_node(self):
        old = NetJsonParser(nodes1)
        new = NetJsonParser(nodes2)
        result = diff(old, new)
        self.assertIsNone(result['removed'])
        self.assertIsInstance(result, dict)
        # ensure node addedly added with properties
        self.assertEqual(len(result['added']['nodes']), 1)
        node = result['added']['nodes'][0]
        self.assertEqual(node['id'], '10.150.0.5')
        self.assertEqual(node['label'], 'node5')
        self.assertEqual(node['local_addresses'], [])
        self.assertEqual(node['properties'], {})
        self.assertIn('10.150.0.5', result['added']['nodes'][0].values())

    def test_changed_3_nodes(self):
        old = NetJsonParser(nodes1)
        new = NetJsonParser(nodes2)
        result = diff(old, new)
        # nodes whose properties have changed
        self.assertEqual(len(result['changed']['nodes']), 3)
        node = result['changed']['nodes'][0]
        self.assertEqual(node['id'], '10.150.0.2')
        self.assertEqual(node['label'], '')
        self.assertEqual(node['local_addresses'], [])
        self.assertEqual(node['properties'], {})
        node = result['changed']['nodes'][1]
        self.assertEqual(node['id'], '10.150.0.3')
        self.assertEqual(node['label'], 'nodeA2')
        self.assertEqual(node['local_addresses'], [])
        self.assertEqual(
            node['properties'],
            {
                'hostname': 'router.2nnx',
                'contact': 'me@project.com',
                'input_octets': 85331213,
                'output_octets': 4358710,
            },
        )
        node = result['changed']['nodes'][2]
        self.assertEqual(node['id'], '10.150.0.4')
        self.assertEqual(node['label'], '')
        self.assertEqual(node['local_addresses'], ['192.168.1.3'])
        self.assertEqual(node['properties'], {'hostname': 'router4.nnx'})

    def test_changed_2_links(self):
        old = NetJsonParser(nodes1)
        new = NetJsonParser(nodes2)
        result = diff(old, new)
        self.assertEqual(len(result['changed']['links']), 2)
        link = result['changed']['links'][0]
        self.assertEqual(link['source'], '10.150.0.3')
        self.assertEqual(link['target'], '10.150.0.2')
        self.assertEqual(link['cost'], 28334)
        self.assertEqual(link['cost_text'], 'Fast link')
        self.assertEqual(link['properties'], {"custom_property": True, "foo": "bar"})
        link = result['changed']['links'][1]
        self.assertEqual(link['source'], '10.150.0.3')
        self.assertEqual(link['target'], '10.150.0.4')
        self.assertEqual(link['cost'], 1048)
        self.assertEqual(link['cost_text'], '')
        self.assertEqual(link['properties'], {})
