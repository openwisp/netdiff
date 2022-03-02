import os

from netdiff import NetJsonParser, diff
from netdiff.tests import TestCase

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
links2 = open('{0}/static/netjson-2-links.json'.format(CURRENT_DIR)).read()


class TestUtils(TestCase):
    """tests for netdiff.utils"""

    def test_same_nodes_but_added_links(self):
        """
        See issue 36:
        https://github.com/ninuxorg/netdiff/issues/36
        """
        old = NetJsonParser(
            {
                "type": "NetworkGraph",
                "protocol": "OLSR",
                "version": "0.6.6",
                "revision": "5031a799fcbe17f61d57e387bc3806de",
                "metric": "ETX",
                "nodes": [
                    {
                        "id": "10.150.0.3",
                        "local_addresses": ["192.168.1.3"],
                        "properties": {"hostname": "router.3nnx"},
                    },
                    {
                        "id": "10.150.0.2",
                        "local_addresses": ["192.168.1.2"],
                        "properties": {"hostname": "router2.nnx"},
                    },
                    {
                        "id": "10.150.0.4",
                        "local_addresses": ["192.168.1.3"],
                        "properties": {"hostname": "router4.nnx"},
                    },
                ],
                "links": [],
            }
        )
        new = NetJsonParser(links2)
        result = diff(old, new)
        self.assertIsNone(result['removed'])
        self.assertEqual(len(result['changed']['nodes']), 2)
        self.assertEqual(len(result['changed']['links']), 0)
        self.assertIsNotNone(result['added'])
        self.assertEqual(len(result['added']['links']), 2)
        self.assertEqual(len(result['added']['nodes']), 0)

    def test_same_nodes_but_removed_links(self):
        """
        See issue 36:
        https://github.com/ninuxorg/netdiff/issues/36
        """
        old = NetJsonParser(
            {
                "type": "NetworkGraph",
                "protocol": "OLSR",
                "version": "0.6.6",
                "revision": "5031a799fcbe17f61d57e387bc3806de",
                "metric": "ETX",
                "nodes": [{"id": "10.150.0.3"}, {"id": "10.150.0.2"}],
                "links": [{"source": "10.150.0.3", "target": "10.150.0.2", "cost": 1}],
            }
        )
        new = NetJsonParser(
            {
                "type": "NetworkGraph",
                "protocol": "OLSR",
                "version": "0.6.6",
                "revision": "5031a799fcbe17f61d57e387bc3806de",
                "metric": "ETX",
                "nodes": [{"id": "10.150.0.3"}, {"id": "10.150.0.2"}],
                "links": [],
            }
        )
        result = diff(old, new)
        self.assertIsNone(result['changed'])
        self.assertIsNone(result['added'])
        self.assertIsNotNone(result['removed'])
        self.assertEqual(len(result['removed']['nodes']), 0)
        self.assertEqual(len(result['removed']['links']), 1)
