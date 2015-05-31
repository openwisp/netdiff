import networkx

from .base import BaseParser
from ..exceptions import ParserError


class Bmx6Parser(BaseParser):
    """ Bmx6_b6m parser """
    protocol = 'BMX6_b6m'
    version = '0'
    metric = 'none'

    def parse(self, data):
        """
        Converts a topology in a NetworkX Graph object.
        """
        # initialize graph and list of aggregated nodes
        graph = networkx.Graph()
        if len(data) != 0:
            if "links" not in data[0]:
                raise ParserError('Parse error, "links" key not found')
        # loop over topology section and create networkx graph
        # this topology don't have weight, so we set it as 1
        for node in data:
            for neigh in node['links']:
                if not graph.has_edge(node['name'], neigh['name']):
                    graph.add_edge(node['name'], neigh['name'], weight=1)
        self.graph = graph
