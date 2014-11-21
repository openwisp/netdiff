import json
import networkx

from netdiff.base import BaseParser


class BatmanParser(BaseParser):
    """ Batman Topology Parser """
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

    def _parse(self, data):
        """
        Converts a topology in a NetworkX Graph object.

        :param str topology: The Batman topology to be converted (JSON or dict)
        :return: the NetworkX Graph object
        """
        # if data is not a python dict it must be a json string
        if type(data) is not dict:
            data = json.loads(data)
        # initialize graph and list of aggregated nodes
        graph = networkx.Graph()
        ag_nodes = self._get_ag_node_list(data['vis'])
        # loop over topology section and create networkx graph
        for node in data["vis"]:
            for neigh in node["neighbors"]:
                p_neigh = self._get_primary(neigh['neighbor'], ag_nodes)
                if not graph.has_edge(node['primary'], p_neigh):
                    graph.add_edge(node['primary'],
                                   p_neigh,
                                   weight=neigh['metric'])
        return graph
