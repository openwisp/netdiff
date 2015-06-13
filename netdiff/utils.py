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
    changed_edges = _find_changed(old.graph, new.graph)
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
    if changed_edges:
        changed = netjson_networkgraph(protocol, version, revision, metric,
                                       [],
                                       changed_edges,
                                       dict=True)
    else:
        changed = None
    return {
        "added": added,
        "removed": removed,
        "changed": changed
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
    old_edges = [set(edge) for edge in old.edges()]
    new_edges = [set(edge) for edge in new.edges()]
    # keep only new links in the graph
    for old_edge in old_edges:
        if old_edge in new_edges:
            not_different.append(tuple(old_edge))
    diff_edges.remove_edges_from(not_different)
    # repeat operation with nodes
    diff_nodes = old.copy()
    not_different = []
    for old_node in old.nodes():
        if old_node in new.nodes():
            not_different.append(old_node)
    diff_nodes.remove_nodes_from(not_different)
    # return tuple with modified graphs
    # one for nodes and one for links
    return diff_nodes, diff_edges


def _find_changed(old, new):
    """
    find changes in link weight
    """
    # find edges that are in both old and new
    both = []
    old_edges = [set(edge) for edge in old.edges()]
    new_edges = [set(edge) for edge in new.edges()]
    for old_edge in old_edges:
        if old_edge in new_edges:
            both.append(tuple(old_edge))
    # create two sets of old and new edges including weight
    old_edges = []
    for edge in old.edges(data=True):
        # skip links that are not in both
        if tuple((edge[0], edge[1])) not in both:
            continue
        dict_edge = {
            'source': edge[0],
            'target': edge[1],
            'weight': edge[2]['weight']
        }
        # let's convert doct to a hashable form
        hashable = tuple(sorted(dict_edge.items()))
        old_edges.append(set(hashable))
    new_edges = []
    for edge in new.edges(data=True):
        # skip links that are not in both
        if tuple((edge[0], edge[1])) not in both:
            continue
        dict_edge = {
            'source': edge[0],
            'target': edge[1],
            'weight': edge[2]['weight']
        }
        # let's convert doct to a hashable form
        hashable = tuple(sorted(dict_edge.items()))
        new_edges.append(set(hashable))
    # find out which edge changed
    changed = []
    for new_edge in new_edges:
        if new_edge not in old_edges:
            d = dict(tuple(new_edge))
            changed.append((d['source'], d['target'], {'weight': d['weight']}))
    return changed
