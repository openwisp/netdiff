import os

from freezegun import freeze_time

from netdiff import WireguardParser, diff
from netdiff.exceptions import ParserError
from netdiff.tests import TestCase

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
wg_dump = open('{0}/static/wg-dump.txt'.format(CURRENT_DIR)).read()
wg_dump_updated = open('{0}/static/wg-dump-2.txt'.format(CURRENT_DIR)).read()


class TestWireguardParser(TestCase):
    def setUp(self):
        self.freezer = freeze_time('2022-06-06 17:03:38')
        self.freezer.start()
        return super().setUp()

    def tearDown(self):
        self.freezer.stop()
        return super().tearDown()

    def test_parse(self):
        p = WireguardParser(wg_dump)
        original_data = p.original_data
        self.assertEqual(list(original_data.keys()), ['wg0', 'wg1'])
        self.assertEqual(
            list(original_data['wg0'].keys()),
            ['publicKey', 'listenPort', 'fwmark', 'peers'],
        )
        self.assertEqual(
            list(original_data['wg0']['peers'][0].values()),
            [
                {
                    'presharedKey': None,
                    'endpoint': '192.168.200.210:41100',
                    'latestHandshake': '2022-06-06T17:03:38Z',
                    'transferRx': '37384',
                    'transferTx': '35848',
                    'persistentKeepalive': 'off',
                    'allowedIps': ['10.254.0.2/32'],
                    'connected': True,
                }
            ],
        )
        self.assertEqual(len(original_data['wg0']['peers']), 8)
        self.assertEqual(len(original_data['wg1']['peers']), 2)
        graph = p.graph
        self.assertIsNotNone(graph)
        self.assertEqual(len(graph.nodes), 7)
        self.assertEqual(len(graph.edges), 5)

    def test_parse_exception(self):
        with self.assertRaises(ParserError):
            WireguardParser('WRONG')

    def test_empty_dict(self):
        WireguardParser(data={})

    def test_wireguard_link_update(self):
        old = WireguardParser(wg_dump)
        new = WireguardParser(wg_dump_updated)
        result = diff(old, new)
        with self.subTest('test links addition'):
            added = result.get('added')
            links = added.get('links')
            self.assertEqual(len(links), 1)
            self.assertEqual(links[0].get('source'), 'wg0')
        with self.subTest('test links deletion'):
            removed = result.get('removed')
            links = removed.get('links')
            self.assertEqual(len(links), 1)
            self.assertEqual(links[0].get('source'), 'wg1')
        with self.subTest('test links modification'):
            changed = result.get('changed')
            nodes = changed.get('nodes')
            links = changed.get('links')
            self.assertEqual(len(nodes), 1)
            self.assertEqual(len(links), 0)
            self.assertEqual(
                nodes[0].get('id'), 'w6xev2DEpaxqgGIOVh8Ggmmr8BYsTEnSpy/3EQ9DfQw='
            )
