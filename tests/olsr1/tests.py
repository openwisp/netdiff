import os
import unittest
import random
import networkx as nx
from netdiff.olsr1 import Olsr1Parser


__all__ = ['TestOlsr1Parser']


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
topology1 = open('{0}/topology1.json'.format(CURRENT_DIR)).read()


class TestOlsr1Parser(unittest.TestCase):

    def test_nochanges(self):
        parser = Olsr1Parser(old=topology1, new=topology1)
        result = parser.diff()
        self.assertTrue(type(result) is dict)
        # TODO:
        # ensure added and removed have 0 changes
