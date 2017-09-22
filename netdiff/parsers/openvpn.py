import networkx
from openvpn_status import parse_status

from .base import BaseParser


class OpenvpnParser(BaseParser):
    """ OpenVPN status log parser """
    protocol = 'OpenVPN Status Log'
    version = '1'
    metric = 'static'
    # for internal use only
    _server_common_name = 'openvpn-server'

    def to_python(self, data):
        return parse_status(data)

    def parse(self, data):
        """
        Converts a OpenVPN JSON to a NetworkX Graph object
        which is then returned.
        """
        # initialize graph and list of aggregated nodes
        graph = networkx.Graph()
        server = self._server_common_name
        # add server (central node) to graph
        graph.add_node(server)
        # add clients in graph as nodes
        for common_name, client in data.client_list.items():
            client_properties = {
                'real_address': str(client.real_address.host),
                'port': client.real_address.port,
                'connected_since': client.connected_since.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'bytes_received': client.bytes_received,
                'bytes_sent': client.bytes_sent
            }
            if common_name in data.routing_table:
                client_properties['local_addresses'] = [
                    str(data.routing_table.get(common_name).virtual_address)
                ]
            graph.add_node(common_name, **client_properties)
        # add links in routing table to graph
        for common_name, link in data.routing_table.items():
            graph.add_edge(server, common_name, weight=1)
        return graph
