import json


class BaseParser(object):
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
            "added": self._make_diff(self.new_graph, self.old_graph, False),
            "removed": self._make_diff(self.old_graph, self.new_graph, False)
        }

    def diff_json(self, **kwargs):
        """
        Returns netdiff in a JSON string
        """
        return json.dumps(self.diff(), **kwargs)

    # --- private methods --- #

    def _parse(self):
        raise NotImplementedError()

    def _make_diff(self, old, new, cost):
        """
        calculates differences between topologies 'old' and 'new'
        if cost is False: No Metric is used to make the diff.
        otherwise, we use cost as a tolerance factor.
        returns a list of links
        """
        # make a copy of old topology to avoid tampering with it
        diff = old.copy()
        not_different = []
        # loop over all links
        for oedge in old.edges():
            # if link is also in new topology add it to the list
            for nedge in new.edges():
                if (oedge[0] in nedge and oedge[1] in nedge):
                    if(not cost):
                        not_different.append(oedge)
                    else:
                        # we check if the old link metric is inside of the
                        # tolerance window
                        if(nedge[3]/cost <= oedge[3] <= nedge[3]*cost):
                            not_different.append(oedge)
        # keep only differences
        diff.remove_edges_from(not_different)
        # return list of links
        return diff.edges()
