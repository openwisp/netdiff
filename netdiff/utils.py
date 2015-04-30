def _make_diff(old, new, cost):
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
    for old_edge in old.edges(data=True):
        # if link is also in new topology add it to the list
        for new_edge in new.edges(data=True):
            if old_edge[0] in new_edge and old_edge[1] in new_edge:
                if not cost:
                    not_different.append(old_edge)
                else:
                    # check if the old link metric is inside of the
                    # tolerance windows
                    if(new_edge[2]['weight'] / cost
                       <= old_edge[2]['weight'] <=
                       new_edge[2]['weight'] * cost):
                        not_different.append(old_edge)
    # keep only differences
    diff.remove_edges_from(not_different)
    # return list of links
    if not cost:
        return diff.edges()
    else:
        # if cost is not false return the edges with the data
        return diff.edges(data=True)


def diff(old, new, cost=False):
    """
    Returns netdiff in a python dictionary
    """
    return {
        "added": _make_diff(new.graph, old.graph, cost),
        "removed": _make_diff(old.graph, new.graph, cost)
    }