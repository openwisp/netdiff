import json
from collections import OrderedDict

from .exceptions import NetJsonError


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
    in_both = _find_unchanged(old.graph, new.graph)
    added_nodes, added_edges = _make_diff(old.graph, new.graph, in_both)
    removed_nodes, removed_edges = _make_diff(new.graph, old.graph, in_both)
    changed_edges = _find_changed(old.graph, new.graph, in_both)
    # create netjson objects
    # or assign None if no changes
    if added_nodes.nodes() and added_edges.edges():
        added = _netjson_networkgraph(protocol, version, revision, metric,
                                      added_nodes.nodes(data=True),
                                      added_edges.edges(data=True),
                                      dict=True)
    else:
        added = None
    if removed_nodes.nodes() and removed_edges.edges():
        removed = _netjson_networkgraph(protocol, version, revision, metric,
                                        removed_nodes.nodes(data=True),
                                        removed_edges.edges(data=True),
                                        dict=True)
    else:
        removed = None
    if changed_edges:
        changed = _netjson_networkgraph(protocol, version, revision, metric,
                                        [],
                                        changed_edges,
                                        dict=True)
    else:
        changed = None
    return OrderedDict((
        ('added', added),
        ('removed', removed),
        ('changed', changed)
    ))


def _make_diff(old, new, both):
    """
    calculates differences between topologies 'old' and 'new'
    returns a tuple with two network graph objects
    the first graph contains the added nodes, the secnod contains the added links
    """
    # make a copy of old topology to avoid tampering with it
    diff_edges = new.copy()
    not_different = [tuple(edge) for edge in both]
    diff_edges.remove_edges_from(not_different)
    # repeat operation with nodes
    diff_nodes = new.copy()
    not_different = []
    for new_node in new.nodes():
        if new_node in old.nodes():
            not_different.append(new_node)
    diff_nodes.remove_nodes_from(not_different)
    # return tuple with modified graphs
    # one for nodes and one for links
    return diff_nodes, diff_edges


def _find_unchanged(old, new):
    """
    returns edges that are in both old and new
    """
    edges = []
    old_edges = [set(edge) for edge in old.edges()]
    new_edges = [set(edge) for edge in new.edges()]
    for old_edge in old_edges:
        if old_edge in new_edges:
            edges.append(set(old_edge))
    return edges


def _find_changed(old, new, both):
    """
    returns links that have changed cost
    """
    # create two list of sets of old and new edges including cost
    old_edges = []
    for edge in old.edges(data=True):
        # skip links that are not in both
        if set((edge[0], edge[1])) not in both:
            continue
        # wrap cost in tuple so it will be recognizable
        cost = (edge[2]['weight'],)
        old_edges.append(set((edge[0], edge[1], cost)))
    new_edges = []
    for edge in new.edges(data=True):
        # skip links that are not in both
        if set((edge[0], edge[1])) not in both:
            continue
        # wrap cost in tuple so it will be recognizable
        cost = (edge[2]['weight'],)
        new_edges.append(set((edge[0], edge[1], cost)))
    # find out which edge changed
    changed = []
    for new_edge in new_edges:
        if new_edge not in old_edges:
            # new_edge is a set, convert it to list
            new_edge = list(new_edge)
            for item in new_edge:
                if isinstance(item, tuple):
                    # unwrap cost from tuple and put it in a dict
                    cost = {'weight': item[0]}
                    new_edge.remove(item)
            changed.append((new_edge[0], new_edge[1], cost))
    return changed


def _netjson_networkgraph(protocol, version, revision, metric,
                          nodes, links,
                          dict=False, **kwargs):
    # netjson format validity check
    if protocol is None:
        raise NetJsonError('protocol cannot be None')
    if version is None and protocol != 'static':
        raise NetJsonError('version cannot be None except when protocol is "static"')
    if metric is None and protocol != 'static':
        raise NetJsonError('metric cannot be None except when protocol is "static"')
    # prepare nodes
    node_list = []
    for node in nodes:
        netjson_node = OrderedDict({'id': node[0]})
        # must copy properties dict to avoid modifying data
        properties = node[1].copy()
        local_addresses = properties.pop('local_addresses', None)
        # append local_addresses only if not empty
        if local_addresses:
            netjson_node['local_addresses'] = local_addresses
        # append properties only if not empty
        if properties:
            netjson_node['properties'] = properties
        node_list.append(netjson_node)
    # prepare links
    link_list = []
    for link in links:
        # must copy properties dict to avoid modifying data
        properties = link[2].copy()
        cost = properties.pop('weight')
        netjson_link = OrderedDict((
            ('source', link[0]),
            ('target', link[1]),
            ('cost', cost)
        ))
        # append properties only if not empty
        if properties:
            netjson_link['properties'] = properties
        link_list.append(netjson_link)
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
