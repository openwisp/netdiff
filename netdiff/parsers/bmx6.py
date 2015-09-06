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
        Converts a BMX6 b6m JSON to a NetworkX Graph object
        which is then returned.
        """
        # initialize graph and list of aggregated nodes
        graph = networkx.Graph()
        if len(data) != 0:
            if "links" not in data[0]:
                raise ParserError('Parse error, "links" key not found')
        # loop over topology section and create networkx graph
        # this data structure does not contain cost information, so we set it as 1
        for node in data:
            for neigh in node['links']:
                graph.add_edge(node['name'], neigh['name'], weight=1)
        return graph
