import networkx
from openvpn_status import ParsingError, parse_status

from ..exceptions import ConversionException, ParserError
from .base import BaseParser


class OpenvpnParser(BaseParser):
    """ OpenVPN status log parser """
    protocol = 'openvpn'
    server_address = '127.0.0.1' # Testing purposes
    version = '1'
    metric = '0'

    def to_python(self, data):
        status = parse_status(data)
        nodes = []
        for i in status.client_list:
            node = status.client_list[i]
            nodes.append({
                'commonName': node.common_name,
                'bytesSent': node.bytes_sent,
                'bytesReceived': node.bytes_received,
                'connectedSince': node.connected_since,
                'realAddress': str(node.real_address)
            })

        return {
            'type': 'OpenVPN',
            'nodes': nodes,
            'updated_at': status.updated_at,
            'server': self.server_address
        }

    def parse(self, data):
        """
        Converts a OpenVPN JSON to a NetworkX Graph object
        which is then returned.
        """
        # initialize graph and list of aggregated nodes
        graph = networkx.Graph()
        if 'type' not in data or data['type'] != 'OpenVPN':
            raise ParserError('Parse Error, not a OpenVPN object')
        required_keys = ['nodes', 'server']
        for key in required_keys:
            if key not in data:
                raise ParserError('Parse Error, "%s" key not found' % key)

        graph.add_node(data['server'])
        for link in data['nodes']:
            try:
                source = data['server']
                target = link['realAddress']
            except KeyError as e:
                raise ParserError('Parse Error, "%s" key not found' % key)
            graph.add_node(target)
            graph.add_edge(source, target, weight=1)
        return graph
