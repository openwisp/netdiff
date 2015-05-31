import networkx

from .base import BaseParser
from ..exceptions import ParserError


class NetJsonParser(BaseParser):
    """ NetJSON (0.1) parser """

    def parse(self, data):
        """
        Converts a NetJSON 'NetworkGraph' object in a NetworkX Graph object.
        """
        graph = networkx.Graph()
        # ensure is NetJSON NetworkGraph object
        if 'type' not in data or data['type'] != 'NetworkGraph':
            raise ParserError('Parse error, not a NetworkGraph object')
        # ensure required keys are present
        required_keys = ['protocol', 'version', 'metric', 'nodes', 'links']
        for key in required_keys:
            if key not in data:
                raise ParserError('Parse error, "{0}" key not found'.format(key))
        # store metadata
        self.protocol = data['protocol']
        self.version = data['version']
        self.revision = data.get('revision')  # optional
        self.metric = data['metric']
        # add nodes
        for node in data['nodes']:
            graph.add_node(node['id'])
        for link in data['links']:
            try:
                source = link["source"]
                dest = link["target"]
                cost = link["weight"]
            except KeyError as e:
                raise ParserError('Parse error, "%s" key not found' % e)
            graph.add_edge(source, dest, weight=cost)
        self.graph = graph
