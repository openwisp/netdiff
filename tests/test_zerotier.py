import os
from json import loads

import networkx

from netdiff import ZeroTierParser, diff
from netdiff.exceptions import ConversionException
from netdiff.tests import TestCase

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
zt_peers = loads(open(f'{CURRENT_DIR}/static/zt-peers.json', 'r').read())
zt_peers_diff = loads(open(f'{CURRENT_DIR}/static/zt-peers-diff.json', 'r').read())


class TestZeroTierParser(TestCase):
    def test_parse(self):
        ng1 = ZeroTierParser(zt_peers)
        ng2 = ZeroTierParser(zt_peers_diff)
        # print(ng2.json(indent=4))
