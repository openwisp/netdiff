import os

import networkx

from netdiff import OpenvpnParser, diff
from netdiff.exceptions import ConversionException
from netdiff.tests import TestCase

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
links2 = open('{0}/static/openvpn-2-links.txt'.format(CURRENT_DIR)).read()
links5_tap = open('{0}/static/openvpn-5-links-tap.txt'.format(CURRENT_DIR)).read()


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
        # check presence of labels
        labels = []
        for node in data['nodes']:
            if 'label' in node:
                labels.append(node['label'])
        self.assertEqual(len(labels), 2)
        self.assertIn('nodeA', labels)
        self.assertIn('nodeB', labels)

    def test_json_dict_tap(self):
        p = OpenvpnParser(links5_tap)
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
        labels = []
        for node in data['nodes']:
            if 'label' in node:
                labels.append(node['label'])
        self.assertEqual(len(labels), 5)
        self.assertIn('nodeA', labels)
        self.assertIn('nodeB', labels)
        self.assertIn('nodeC', labels)
        self.assertIn('nodeD', labels)
        self.assertIn('nodeE', labels)

    def test_empty_string(self):
        OpenvpnParser(data='{}')

    def test_bogus_data(self):
        try:
            OpenvpnParser(data='{%$^*([[zsde4323@#}')
        except ConversionException as e:
            print("Something went wrong: {0}".format(str(e)))
        else:
            self.fail('ValidationError not raised')

    def test_empty_dict(self):
        OpenvpnParser({})

    def test_label_diff_added(self):
        old = OpenvpnParser({})
        new = OpenvpnParser(links5_tap)
        result = diff(old, new)
        labels = []
        for node in result['added']['nodes']:
            if 'label' in node:
                labels.append(node['label'])
        self.assertEqual(len(labels), 5)
        self.assertIn('nodeA', labels)
        self.assertIn('nodeB', labels)
        self.assertIn('nodeC', labels)
        self.assertIn('nodeD', labels)
        self.assertIn('nodeE', labels)
