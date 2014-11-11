import os
import unittest
import random
import networkx as nx
from netdiff.olsr1 import Olsr1Parser
from .Olsr_graph_gen import OlsrGraphGen


__all__ = ['TestOlsr1Parser']


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
topology1 = open('{0}/topology1.json'.format(CURRENT_DIR)).read()


class TestOlsr1Parser(unittest.TestCase):
    og = OlsrGraphGen(topology1)
    def test_nochanges(self):
        parser = Olsr1Parser(old=topology1, new=topology1)
        result = parser.diff()
        self.assertTrue(type(result) is dict)
        # TODO:
        # ensure added and removed have 0 changes

    def test_different_leo(self):
        for n in range(20,len(self.og.graph)):
            parser = Olsr1Parser(old = topology1, new = self.og.gen_olsr_topo(self.og.reduce_graph(n)))
            result = parser.diff()
            self.assertFalse((len(result['removed'].edges())==0) and
                             (len(result['added'].edges())==0))
        self.assertTrue(1)

    def small_graph_test(self):
        old_graph = self.og.gen_olsr_topo(self.og.reduce_graph(10))
        new_graph = self.og.gen_olsr_topo(self.og.reduce_graph(15))
        parser = Olsr1Parser(old=old_graph, new = new_graph)
        result = parser.diff();
        self.assertTrue((len(result['removed'].edges())>0) or
                         (len(result['added'].edges())>0))
