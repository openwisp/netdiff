import json
import networkx


class Olsr1Parser(object):
    """ OLSR v1 Topology Parser """

    def __init__(self, old, new):
        """
        Initializes a new Olsr1Parser

        :param str old: a JSON or dict representing the old OLSR1 topology
        :param str new: a JSON or dict representing the new OLSR1 topology
        """
        self.old_graph = self._parse(old)
        self.new_graph = self._parse(new)

    def diff(self):
        """
        Returns netdiff in a python dictionary
        """
        return {
            "added": self._make_diff(self.new_graph, self.old_graph),
            "removed": self._make_diff(self.old_graph, self.new_graph)
        }

    def diff_json(self, **kwargs):
        """
        Returns netdiff in a JSON string
        """
        return json.dumps(self.diff(), **kwargs)

    # --- private methods --- #

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

    def _make_diff(self, old, new):
        """
        calculates differences between topologies 'old' and 'new'
        returns a list of links
        """
        # make a copy of old topology to avoid tampering with it
        diff = old.copy()
        not_different = []
        # loop over all links
        for edge in old.edges():
            # if link is also in new topology add it to the list
            if edge in new.edges():
                not_different.append(edge)
        # keep only differences
        diff.remove_edges_from(not_different)
        # return list of links
        return diff.edges()
