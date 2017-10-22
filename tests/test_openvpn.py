import os

import networkx
import six
from netdiff import OpenvpnParser
from netdiff.tests import TestCase

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
links2 = open('{0}/static/openvpn-2-links.txt'.format(CURRENT_DIR)).read()
links2_tap = open('{0}/static/openvpn-5-links-tap.txt'.format(CURRENT_DIR)).read()


class TestOpenvpnParser(TestCase):

    def test_parse(self):
        p = OpenvpnParser(links2)
        self.assertIsInstance(p.graph, networkx.Graph)
        self.assertEqual(p.version, '1')
        self.assertEqual(p.metric, 'static')

    def test_json_dict(self):
        p = OpenvpnParser(links2)
        data = p.json(dict=True)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['type'], 'NetworkGraph')
        self.assertEqual(data['protocol'], 'OpenVPN Status Log')
        self.assertEqual(data['version'], '1')
        self.assertEqual(data['revision'], None)
        self.assertEqual(data['metric'], 'static')
        self.assertIsInstance(data['nodes'], list)
        self.assertIsInstance(data['links'], list)
        self.assertEqual(len(data['nodes']), 3)
        self.assertEqual(len(data['links']), 2)

    def test_json_dict_tap(self):
        p = OpenvpnParser(links2_tap)
        data = p.json(dict=True)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['type'], 'NetworkGraph')
        self.assertEqual(data['protocol'], 'OpenVPN Status Log')
        self.assertEqual(data['version'], '1')
        self.assertEqual(data['revision'], None)
        self.assertEqual(data['metric'], 'static')
        self.assertIsInstance(data['nodes'], list)
        self.assertIsInstance(data['links'], list)
        self.assertEqual(len(data['nodes']), 6)
        self.assertEqual(len(data['links']), 5)
