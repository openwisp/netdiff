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
    nodes_in_both, edges_in_both = _find_unchanged(old.graph, new.graph)
    added_nodes, added_edges = _make_diff(old.graph, new.graph, edges_in_both)
    removed_nodes, removed_edges = _make_diff(new.graph, old.graph, edges_in_both)
    changed_nodes = _find_changed_nodes(old.graph, new.graph, nodes_in_both)
    changed_edges = _find_changed_edges(old.graph, new.graph, edges_in_both)
    # create netjson objects
    # or assign None if no changes
    if added_nodes.nodes() or added_edges.edges():
        added = _netjson_networkgraph(
            protocol,
            version,
            revision,
            metric,
            added_nodes.nodes(data=True),
            added_edges.edges(data=True),
            dict=True,
        )
    else:
        added = None
    if removed_nodes.nodes() or removed_edges.edges():
        removed = _netjson_networkgraph(
            protocol,
            version,
            revision,
            metric,
            removed_nodes.nodes(data=True),
            removed_edges.edges(data=True),
            dict=True,
        )
    else:
        removed = None
    if changed_nodes or changed_edges:
        changed = _netjson_networkgraph(
            protocol, version, revision, metric, changed_nodes, changed_edges, dict=True
        )
    else:
        changed = None
    return OrderedDict((('added', added), ('removed', removed), ('changed', changed)))


def _make_diff(old, new, both):
    """
    calculates differences between topologies 'old' and 'new'
    returns a tuple with two network graph objects
    the first graph contains the added nodes, the second contains the added links
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
    returns nodes and edges that are in both old and new
    """
    edges = []
    nodes = []
    old_edges = [set([src, dst]) for src, dst in old.edges()]
    new_edges = [set([src, dst]) for src, dst in new.edges()]
    old_nodes = [node for node in old.nodes()]
    new_nodes = [node for node in new.nodes()]
    for old_edge in old_edges:
        if old_edge in new_edges:
            edges.append(set(old_edge))
    for old_node in old_nodes:
        if old_node in new_nodes:
            nodes.append(old_node)
    return nodes, edges


def _nodes_difference(graph, both):
    nodes = []
    for ip, properties in graph.nodes(data=True):
        # skip nodes that are not in both
        if ip not in both:
            continue
        props = properties.copy()
        old_node = [ip]
        # wrap attributes in tuples so they will be recognizable
        old_node.append(('label', popdefault(props, 'label', '')))
        old_node.append(('local_addresses', props.pop('local_addresses', [])))
        for name, value in props.items():
            old_node.append((name, value))
        nodes.append(old_node)
    return nodes


def _find_changed_nodes(old, new, both):
    """
    returns nodes that have changed properties
    """
    # create two list of sets of old and new nodes including
    # label, local_addresses and properties
    old_nodes = _nodes_difference(old, both)
    new_nodes = _nodes_difference(new, both)

    # find out which node changed
    changed = []
    for new_node in new_nodes:
        if new_node not in old_nodes:
            props = {}
            for item in new_node:
                if isinstance(item, tuple):
                    props[item[0]] = item[1]
            changed.append((new_node[0], props))
    return changed


def _edges_difference(graph, both):
    edges = []
    for src, dst, properties in graph.edges(data=True):
        # skip edges that are not in both
        if set((src, dst)) not in both:
            continue
        props = properties.copy()
        old_edge = [('_src', src), ('_dst', dst)]
        old_edge.append(('weight', props.pop('weight')))
        old_edge.append(('cost_text', props.pop('cost_text', '')))
        for name, value in props.items():
            old_edge.append((name, value))
        edges.append(set(old_edge))
    return edges


def _find_changed_edges(old, new, both):
    """
    returns links that have changed any attribute
    """
    # create two list of sets of old and new edges including
    # cost, cost_text and properties
    old_edges = _edges_difference(old, both)
    new_edges = _edges_difference(new, both)

    # find out which edge changed
    changed = []
    for new_edge in new_edges:
        if new_edge not in old_edges:
            props = dict(new_edge)
            src = props.pop('_src')
            dst = props.pop('_dst')
            changed.append([src, dst, props])
    return changed


def popdefault(dictionary, key, default):
    """
    If the key is present and the value is not None, return it.
    If the key is present and the value is None, return ``default`` instead.
    If the key is not present, return ``default`` too.
    """
    value = dictionary.pop(key, None)
    return value or default


def _netjson_networkgraph(
    protocol, version, revision, metric, nodes, links, dict=False, **kwargs
):
    # netjson format validity check
    if protocol is None:
        raise NetJsonError('protocol cannot be None')
    if version is None and protocol != 'static':
        raise NetJsonError('version cannot be None except when protocol is "static"')
    # prepare nodes
    node_list = []
    for ip, properties in nodes:
        netjson_node = OrderedDict({'id': ip})
        # must copy properties dict to avoid modifying data
        props = properties.copy()
        netjson_node['label'] = popdefault(props, 'label', '')
        netjson_node['local_addresses'] = popdefault(props, 'local_addresses', [])
        netjson_node['properties'] = props
        node_list.append(netjson_node)
    node_list.sort(key=lambda d: d['id'])
    # prepare links
    link_list = []
    for source, target, properties in links:
        # must copy properties dict to avoid modifying data
        props = properties.copy()
        netjson_link = OrderedDict((('source', source), ('target', target)))
        netjson_link['cost'] = props.pop('weight')
        netjson_link['cost_text'] = popdefault(props, 'cost_text', '')
        netjson_link['properties'] = props
        link_list.append(netjson_link)
    link_list.sort(key=lambda d: (d['source'], d['target']))
    data = OrderedDict(
        (
            ('type', 'NetworkGraph'),
            ('protocol', protocol),
            ('version', version),
            ('revision', revision),
            ('metric', metric),
            ('nodes', node_list),
            ('links', link_list),
        )
    )
    if dict:
        return data
    return json.dumps(data, **kwargs)
