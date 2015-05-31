import networkx

from .base import BaseParser
from ..exceptions import ParserError


class BatmanParser(BaseParser):
    """ batman-adv parser """
    protocol = 'batman-adv'
    version = '2015.0'
    metric = 'TQ'

    def _get_primary(self, mac, collection):
        # Use the ag_node structure to return the main mac address associated to
        # a secondary mac, if none return itself.
        for node in collection:
            for interface in node:
                if mac == interface:
                    return node[0]
        return 0

    def _get_ag_node_list(self, data):
        # Create a structure of main and secondary mac address.
        ag_nodes = []
        for node in data:
            ag_interfaces = []
            ag_interfaces.append(node['primary'])
            if('secondary'in node):
                for interface in node['secondary']:
                    ag_interfaces.append(interface)
            ag_nodes.append(ag_interfaces)
        return ag_nodes

    def parse(self, data):
        """
        Converts a topology in a NetworkX Graph object.
        """
        # initialize graph and list of aggregated nodes
        graph = networkx.Graph()
        if 'source_version' in data:
            self.version = data['source_version']
        if 'vis' not in data:
            raise ParserError('Parse error, "vis" key not found')
        ag_nodes = self._get_ag_node_list(data['vis'])
        # loop over topology section and create networkx graph
        for node in data["vis"]:
            for neigh in node["neighbors"]:
                p_neigh = self._get_primary(neigh['neighbor'], ag_nodes)
                if not graph.has_edge(node['primary'], p_neigh):
                    graph.add_edge(node['primary'],
                                   p_neigh,
                                   weight=neigh['metric'])
        self.graph = graph
