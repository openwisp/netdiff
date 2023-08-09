import os

import networkx

from netdiff import ZeroTierParser, diff
from netdiff.exceptions import ConversionException
from netdiff.tests import TestCase

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
zt_peers = open(f'{CURRENT_DIR}/static/zt-peers.json').read()
zt_peers_updated = open(f'{CURRENT_DIR}/static/zt-peers-updated.json').read()


class TestZeroTierParser(TestCase):
    _TEST_PATH_KEYS = [
        'weight',
        'active',
        'address',
        'expired',
        'lastReceive',
        'lastSend',
        'localSocket',
        'preferred',
        'trustedPathId',
    ]
    _TEST_PEER_KEYS = ['label', 'address', 'role', 'version', 'tunneled', 'isBonded']

    def test_parse(self):
        p = ZeroTierParser(zt_peers)
        graph = p.graph
        self.assertEqual(len(graph.nodes), 3)
        self.assertEqual(len(graph.edges), 2)
        self.assertIsInstance(graph, networkx.Graph)
        edges = list(graph.edges(data=True))
        nodes = list(graph.nodes(data=True))
        edge1 = edges[0]
        edge2 = edges[1]
        edge1_properties = edge1[2]
        edge2_properties = edge2[2]
        controller = nodes[0]
        node1 = nodes[1]
        node2 = nodes[2]
        controller_properties = controller[1]
        node1_properties = node1[1]
        node2_properties = node2[1]
        self.assertEqual(edge1[0], 'controller')
        self.assertEqual(edge1[1], '3504e2b2e2')
        self.assertEqual(list(edge1_properties.keys()), self._TEST_PATH_KEYS)
        self.assertEqual(edge2[0], 'controller')
        self.assertEqual(edge2[1], '4a9e1c6f14')
        self.assertEqual(list(edge2_properties.keys()), self._TEST_PATH_KEYS)
        self.assertEqual(controller_properties, {'label': 'controller'})
        self.assertEqual(list(node1_properties.keys()), self._TEST_PEER_KEYS)
        self.assertEqual(list(node2_properties.keys()), self._TEST_PEER_KEYS)

    def test_json_dict(self):
        p = ZeroTierParser(zt_peers)
        data = p.json(dict=True)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['type'], 'NetworkGraph')
        self.assertEqual(data['protocol'], 'ZeroTier Controller Peers')
        self.assertEqual(data['version'], '1')
        self.assertEqual(data['revision'], None)
        self.assertEqual(data['metric'], 'static')
        self.assertIsInstance(data['nodes'], list)
        self.assertIsInstance(data['links'], list)
        self.assertEqual(len(data['nodes']), 3)
        self.assertEqual(len(data['links']), 2)
        # check presence of labels
        labels = []
        for node in data['nodes']:
            if 'label' in node:
                labels.append(node['label'])
        self.assertEqual(len(labels), 3)
        self.assertIn('controller', labels)
        self.assertIn('3504e2b2e2', labels)
        self.assertIn('4a9e1c6f14', labels)

    def test_bogus_data(self):
        try:
            ZeroTierParser(data='{%$^*([[zsde4323@#}')
        except ConversionException:
            pass
        else:
            self.fail('ConversionException not raised')

    def test_empty_dict(self):
        ZeroTierParser(data={})

    def test_no_changes(self):
        old = ZeroTierParser(zt_peers)
        new = ZeroTierParser(zt_peers)
        result = diff(old, new)
        self.assertIsInstance(result, dict)
        self.assertIsNone(result['added'])
        self.assertIsNone(result['removed'])
        self.assertIsNone(result['changed'])

    def test_zerotier_link_update(self):
        old = ZeroTierParser(zt_peers)
        new = ZeroTierParser(zt_peers_updated)
        result = diff(old, new)

        with self.subTest('test links addition'):
            added = result.get('added')
            links = added.get('links')
            self.assertEqual(len(links), 1)
            self.assertEqual(links[0].get('source'), 'controller')
            self.assertEqual(links[0].get('target'), '9a9e1c9f19')

        with self.subTest('test links deletion'):
            removed = result.get('removed')
            links = removed.get('links')
            self.assertEqual(len(links), 1)
            self.assertEqual(links[0].get('source'), 'controller')
            self.assertEqual(links[0].get('target'), '4a9e1c6f14')

        with self.subTest('test links modification'):
            changed = result.get('changed')
            nodes = changed.get('nodes')
            links = changed.get('links')
            # Only link properties have been modified
            self.assertEqual(len(nodes), 0)
            self.assertEqual(len(links), 1)
            self.assertEqual(links[0].get('cost'), 9)
            self.assertEqual(
                links[0].get('properties').get('address'), '192.168.56.1/44221'
            )
