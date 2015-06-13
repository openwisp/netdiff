import json
from collections import OrderedDict

from .exceptions import NetJsonError


def netjson_networkgraph(protocol, version, revision, metric,
                         nodes, links,
                         dict=False, **kwargs):
    # netjson formatting check
    if protocol is None:
        raise NetJsonError('protocol cannot be None')
    if version is None and protocol != 'static':
        raise NetJsonError('version cannot be None except when protocol is "static"')
    if metric is None and protocol != 'static':
        raise NetJsonError('metric cannot be None except when protocol is "static"')
    # prepare lists
    node_list = [{'id': node} for node in nodes]
    link_list = []
    for link in links:
        link_list.append(OrderedDict((
            ('source', link[0]),
            ('target', link[1]),
            ('weight', link[2]['weight'])
        )))
    data = OrderedDict((
        ('type', 'NetworkGraph'),
        ('protocol', protocol),
        ('version', version),
        ('revision', revision),
        ('metric', metric),
        ('nodes', node_list),
        ('links', link_list)
    ))
    if dict:
        return data
    return json.dumps(data, **kwargs)


def diff(old, new):
    """
    Returns differences of two network topologies old and new
    in NetJSON NetworkGraph compatible format
    """
    protocol = new.protocol
    version = new.version
    revision = new.revision
    metric = new.metric
    # calculate differences
    added_nodes, added_edges = _make_diff(new.graph, old.graph)
    removed_nodes, removed_edges = _make_diff(old.graph, new.graph)
    # create netjson objects
    # or assign None if no changes
    if added_nodes.nodes() and added_edges.edges():
        added = netjson_networkgraph(protocol, version, revision, metric,
                                     added_nodes.nodes(),
                                     added_edges.edges(data=True),
                                     dict=True)
    else:
        added = None
    if removed_nodes.nodes() and removed_edges.edges():
        removed = netjson_networkgraph(protocol, version, revision, metric,
                                       removed_nodes.nodes(),
                                       removed_edges.edges(data=True),
                                       dict=True)
    else:
        removed = None
    return {
        "added": added,
        "removed": removed
    }


def _make_diff(old, new):
    """
    calculates differences between topologies 'old' and 'new'
    returns a tuple with two network graph objects
    the first graph contains the added nodes, the secnod contains the added links
    """
    # make a copy of old topology to avoid tampering with it
    diff_edges = old.copy()
    not_different = []
    # keep only new links in the graph
    for old_edge in old.edges(data=True):
        # if link is also in new topology add it to the list
        for new_edge in new.edges(data=True):
            if old_edge[0] in new_edge and old_edge[1] in new_edge:
                not_different.append(old_edge)
    diff_edges.remove_edges_from(not_different)
    # repeat operation with nodes
    diff_nodes = old.copy()
    not_different = []
    for old_node in old.nodes():
        if old_node in new.nodes():
            not_different.append(old_node)
    diff_nodes.remove_nodes_from(not_different)
    # return modified graph
    return diff_nodes, diff_edges
