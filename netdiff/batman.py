import json
import networkx

from netdiff.base import BaseParser


class BatmanParser(BaseParser):
    """ Batman Topology Parser """
    def _get_primary(self, mac, collection):
        for node in collection:
            for interface in node:
                if mac == interface:
                    return node[0]
        return 0

    def _get_ag_node_list(self, data):
        agn = []
        for node in data:
            agi = []
            agi.append(node['primary'])
            if('secondary'in node):
                for interface in node['secondary']:
                    agi.append(interface)
            agn.append(agi)
        return agn

    def _parse(self, data):
        """
        Converts a topology in a NetworkX MultiGraph object.

        :param str topology: The OLSR1 topology to be converted (JSON or dict)
        :return: the NetworkX MultiGraph object
        """
        # if data is not a python dict it must be a json string
        if type(data) is not dict:
            data = json.loads(data)
        # initialize graph and list of aggregated nodes
        graph = networkx.MultiGraph()
        agn = self._get_ag_node_list(data['vis'])
        # loop over topology section and create networkx graph
        for node in data["vis"]:
            for neigh in node["neighbors"]:
                p_neigh = self._get_primary(neigh['neighbor'], agn)
                if not graph.has_edge(node['primary'], p_neigh):
                    graph.add_edge(node['primary'],
                                   p_neigh,
                                   weight=neigh['metric'])
        return graph
