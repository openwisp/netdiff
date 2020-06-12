from ..exceptions import ParserError
from .base import BaseParser


class NetJsonParser(BaseParser):
    """ NetJSON (0.1) parser """

    def parse(self, data):
        """
        Converts a NetJSON 'NetworkGraph' object
        to a NetworkX Graph object,which is then returned.
        Additionally checks for protocol version, revision and metric.
        """
        graph = self._init_graph()
        # ensure is NetJSON NetworkGraph object
        if 'type' not in data or data['type'] != 'NetworkGraph':
            raise ParserError('Parse error, not a NetworkGraph object')
        # ensure required keys are present
        required_keys = ['protocol', 'version', 'metric', 'nodes', 'links']
        for key in required_keys:
            if key not in data:
                raise ParserError('Parse error, "{0}" key not found'.format(key))

        # store metadata
        self.protocol = data['protocol']
        self.version = data['version']
        self.revision = data.get('revision')  # optional
        self.metric = data['metric']

        # create graph
        for node in data['nodes']:
            graph.add_node(
                node['id'],
                label=node['label'] if 'label' in node else None,
                local_addresses=node.get('local_addresses', []),
                **node.get('properties', {})
            )
        for link in data['links']:
            try:
                source = link['source']
                dest = link['target']
                cost = link['cost']
                cost_text = link.get("cost_text", '')
            except KeyError as e:
                raise ParserError('Parse error, "%s" key not found' % e)
            properties = link.get('properties', {})
            graph.add_edge(source, dest, weight=cost, cost_text=cost_text, **properties)
        return graph
