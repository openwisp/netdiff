import json
import networkx


class Parser(object):
    """ Generic Topology Parser """

    def __init__(self, old, new):
        """
        Initializes a new Parser

        :param str old: a JSON or dict representing the old topology
        :param str new: a JSON or dict representing the new topology
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

    def _make_diff(self, old, new):
        """
        calculates differences between topologies 'old' and 'new'
        returns a list of links
        """
        # make a copy of old topology to avoid tampering with it
        diff = old.copy()
        not_different = []
        # loop over all links
        for oedge in old.edges():
            # if link is also in new topology add it to the list
            for nedge in new.edges():
                if ((oedge[0] == nedge[0]) and (oedge[1] == nedge[1])) or ((oedge[1] == nedge[0]) and (oedge[0] == nedge[1])):
                    not_different.append(oedge)
        # keep only differences
        diff.remove_edges_from(not_different)
        # return list of links
        return diff.edges()
