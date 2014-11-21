import json
import networkx
from netdiff.nxparser import Parser


class Olsr1Parser(Parser):
    """ OLSR v1 Topology Parser """
    def _parse(self, topology):
        """
        Converts a topology in a NetworkX MultiGraph object.

        :param str topology: The OLSR1 topology to be converted (JSON or dict)
        :return: the NetworkX MultiGraph object
        """
        # if data is not a python dict it must be a json string
        if type(topology) is not dict:
            topology = json.loads(topology)
        # initialize graph
        graph = networkx.MultiGraph()
        # loop over topology section and create networkx graph
        for link in topology["topology"]:
            graph.add_edge(link["lastHopIP"],
                           link["destinationIP"],
                           weight=link["tcEdgeCost"])
        return graph
