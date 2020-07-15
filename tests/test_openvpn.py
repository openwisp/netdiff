import os

import networkx

from netdiff import OpenvpnParser, diff
from netdiff.exceptions import ConversionException
from netdiff.tests import TestCase

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
links2 = open('{0}/static/openvpn-2-links.txt'.format(CURRENT_DIR)).read()
links2undef = open('{0}/static/openvpn-2-links-undef.txt'.format(CURRENT_DIR)).read()
links5_tap = open('{0}/static/openvpn-5-links-tap.txt'.format(CURRENT_DIR)).read()
bug = open('{0}/static/openvpn-bug.txt'.format(CURRENT_DIR)).read()
special_case = open('{0}/static/openvpn-special-case.txt'.format(CURRENT_DIR)).read()


class TestOpenvpnParser(TestCase):
    def test_parse(self):
        p = OpenvpnParser(links2)
        self.assertIsInstance(p.graph, networkx.Graph)
        self.assertEqual(p.version, '1')
        self.assertEqual(p.metric, 'static')

    def test_parse_undef(self):
        p = OpenvpnParser(links2undef)
        data = p.json(dict=True)
        self.assertIsInstance(p.graph, networkx.Graph)
        # we expect 1 node (only the openvpn server)
        self.assertEqual(len(data['nodes']), 1)
        self.assertEqual(len(data['links']), 0)

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
        self.assertEqual(len(labels), 3)
        self.assertIn('nodeA', labels)
        self.assertIn('nodeB', labels)
        self.assertIn('', labels)

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
        self.assertEqual(len(labels), 6)
        self.assertIn('nodeA', labels)
        self.assertIn('nodeB', labels)
        self.assertIn('nodeC', labels)
        self.assertIn('nodeD', labels)
        self.assertIn('nodeE', labels)
        self.assertIn('', labels)

    def test_bogus_data(self):
        try:
            OpenvpnParser(data='{%$^*([[zsde4323@#}')
        except ConversionException:
            pass
        else:
            self.fail('ConversionException not raised')

    def test_empty_dict(self):
        OpenvpnParser(data={})

    def test_empty_string(self):
        OpenvpnParser(data='')

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

    def test_parse_bug(self):
        p = OpenvpnParser(bug, duplicate_cn=True)
        data = p.json(dict=True)
        self.assertIsInstance(p.graph, networkx.Graph)

        with self.subTest('Count nodes and links'):
            self.assertEqual(len(data['nodes']), 7)
            self.assertEqual(len(data['links']), 6)

        labels = []
        for node in data['nodes']:
            labels.append(node['label'])
        expected = {
            '60c5a8fffe77607a',
            '60c5a8fffe77606b',
            '60C5A8FFFE74CB6D',
            '60c5a8fffe77607a',
            '58a0cbeffe0176d4',
            '58a0cbeffe0156b0',
            '',
        }
        with self.subTest('Check contents of nodes'):
            self.assertEqual(expected, set(labels))

        targets = []
        for link in data['links']:
            targets.append(link['target'])
        expected = {
            '60c5a8fffe77607a,185.211.160.5',
            '60c5a8fffe77606b,185.211.160.87',
            '60C5A8FFFE74CB6D,194.183.10.51',
            '60c5a8fffe77607a,194.183.10.51',
            '58a0cbeffe0176d4,195.94.160.52',
            '58a0cbeffe0156b0,217.72.97.67',
        }
        self.assertEqual(expected, set(targets))

    def test_parse_bug_duplicate_cn(self):
        p = OpenvpnParser(bug, duplicate_cn=True)
        data = p.json(dict=True)
        self.assertIsInstance(p.graph, networkx.Graph)

        with self.subTest('Count nodes and links'):
            self.assertEqual(len(data['nodes']), 7)
            self.assertEqual(len(data['links']), 6)

        labels = []
        for node in data['nodes']:
            labels.append(node['label'])
        expected = {
            '60c5a8fffe77607a',
            '60c5a8fffe77606b',
            '60C5A8FFFE74CB6D',
            '60c5a8fffe77607a',
            '58a0cbeffe0176d4',
            '58a0cbeffe0156b0',
            '',
        }
        with self.subTest('Check contents of nodes'):
            self.assertEqual(expected, set(labels))

        targets = []
        for link in data['links']:
            targets.append(link['target'])
        expected = {
            '60c5a8fffe77607a,185.211.160.5',
            '60c5a8fffe77606b,185.211.160.87',
            '60C5A8FFFE74CB6D,194.183.10.51',
            '60c5a8fffe77607a,194.183.10.51',
            '58a0cbeffe0176d4,195.94.160.52',
            '58a0cbeffe0156b0,217.72.97.67',
        }
        self.assertEqual(expected, set(targets))

    def test_parse_special_case_duplicate_cn(self):
        """
        Tests behavior when the topology contains
        nodes that have the same common name and same address
        (it can happen when allowing reusing the same certificate
         and multiple clients are connected behind the same public IP)
        """
        p = OpenvpnParser(special_case, duplicate_cn=True)
        data = p.json(dict=True)
        self.assertIsInstance(p.graph, networkx.Graph)
        with self.subTest('Count nodes and links'):
            self.assertEqual(len(data['nodes']), 5)
            self.assertEqual(len(data['links']), 4)

        id_list = []
        for node in data['nodes']:
            id_list.append(node['id'])
        expected = {
            '60c5a8fffe77607a,194.183.10.51:49794',
            '60c5a8fffe77607a,194.183.10.51:60003',
            '60c5a8fffe77607a,217.72.97.66',
            '58a0cbeffe0156b0,217.72.97.67',
            'openvpn-server',
        }
        with self.subTest('Check contents of nodes'):
            self.assertEqual(expected, set(id_list))

        targets = []
        for link in data['links']:
            targets.append(link['target'])
        expected = {
            '60c5a8fffe77607a,194.183.10.51:49794',
            '60c5a8fffe77607a,194.183.10.51:60003',
            '60c5a8fffe77607a,217.72.97.66',
            '58a0cbeffe0156b0,217.72.97.67',
        }
        self.assertEqual(expected, set(targets))

    def test_common_name_as_id(self):
        old = OpenvpnParser({})
        new = OpenvpnParser(links5_tap)
        result = diff(old, new)
        id_list = []
        for node in result['added']['nodes']:
            id_list.append(node['id'])
            self.assertEqual(node['id'], node['properties']['common_name'])
        self.assertEqual(len(id_list), 5)
        self.assertIn('nodeA', id_list)
        self.assertIn('nodeB', id_list)
        self.assertIn('nodeC', id_list)
        self.assertIn('nodeD', id_list)
        self.assertIn('nodeE', id_list)
