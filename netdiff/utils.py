def _make_diff(old, new):
    """
    calculates differences between topologies 'old' and 'new'
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
                not_different.append(old_edge)
    # keep only differences
    diff.remove_edges_from(not_different)
    # return list of links
    return diff.edges()


def diff(old, new):
    """
    Returns differences of two network topologies old and new
    """
    return {
        "added": _make_diff(new.graph, old.graph),
        "removed": _make_diff(old.graph, new.graph)
    }
