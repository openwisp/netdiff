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
        real_addresses = []
        special_cases = []
        for client in clients:
            address = client.real_address
            if address.host in real_addresses:
                special_cases.append(address.host)
                continue
            real_addresses.append(address.host)
        # add clients in graph as nodes
        for client in clients:
            if client.common_name == 'UNDEF':
                continue
            address = client.real_address
            client_properties = {
                'label': client.common_name,
                'real_address': str(address.host),
                'port': int(address.port),
                'connected_since': client.connected_since.strftime(
                    '%Y-%m-%dT%H:%M:%SZ'
                ),
                'bytes_received': int(client.bytes_received),
                'bytes_sent': int(client.bytes_sent),
            }
            local_addresses = [
                str(route.virtual_address)
                for route in data.routing_table.values()
                if route.real_address == address
            ]
            if local_addresses:
                client_properties['local_addresses'] = local_addresses
            # use host:port as node ID only when
            # there are more nodes with the same address
            if address.host in special_cases:
                node_id = '{}:{}'.format(address.host, address.port)
            else:
                node_id = str(address.host)
            graph.add_node(node_id, **client_properties)
        # add links in routing table to graph
        for link in links:
            if link.common_name == 'UNDEF':
                continue
            address = link.real_address
            if address.host in special_cases:
                target_id = '{}:{}'.format(address.host, address.port)
            else:
                target_id = str(address.host)
            graph.add_edge(server, str(target_id), weight=1)
        return graph
