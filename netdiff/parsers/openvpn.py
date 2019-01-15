from openvpn_status import parse_status
from openvpn_status.parser import ParsingError

from ..exceptions import ConversionException
from .base import BaseParser


class OpenvpnParser(BaseParser):
    """ OpenVPN status log parser """
    protocol = 'OpenVPN Status Log'
    version = '1'
    metric = 'static'
    # for internal use only
    _server_common_name = 'openvpn-server'

    def to_python(self, data):
        if not data:
            return None
        try:
            return parse_status(data)
        except (AttributeError, ParsingError) as e:
            msg = 'OpenVPN parsing error: {0}'.format(str(e))
            raise ConversionException(msg, data=data)

    def parse(self, data):
        """
        Converts a OpenVPN JSON to a NetworkX Graph object
        which is then returned.
        """
        # initialize graph and list of aggregated nodes
        graph = self._init_graph()
        server = self._server_common_name
        # add server (central node) to graph
        graph.add_node(server)
        # data may be empty
        if data is None:
            clients = []
            links = []
        else:
            clients = data.client_list.values()
            links = data.routing_table.values()
        # add clients in graph as nodes
        for client in clients:
            if client.common_name == 'UNDEF':
                continue
            client_properties = {
                'label': client.common_name,
                'real_address': str(client.real_address.host),
                'port': int(client.real_address.port),
                'connected_since': client.connected_since.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'bytes_received': int(client.bytes_received),
                'bytes_sent': int(client.bytes_sent)
            }
            local_addresses = [
                str(route.virtual_address)
                for route in data.routing_table.values()
                if route.real_address == client.real_address
            ]
            if local_addresses:
                client_properties['local_addresses'] = local_addresses
            graph.add_node(str(client.real_address.host), **client_properties)
        # add links in routing table to graph
        for link in links:
            if link.common_name == 'UNDEF':
                continue
            graph.add_edge(server, str(link.real_address.host), weight=1)
        return graph
