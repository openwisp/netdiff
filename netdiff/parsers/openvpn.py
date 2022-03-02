from openvpn_status import parse_status
from openvpn_status.parser import ParsingError

from ..exceptions import ConversionException
from .base import BaseParser


class OpenvpnParser(BaseParser):
    """OpenVPN status log parser"""

    protocol = 'OpenVPN Status Log'
    version = '1'
    metric = 'static'
    duplicate_cn = False
    # for internal use only
    _server_common_name = 'openvpn-server'

    def __init__(self, *args, **kwargs):
        self.duplicate_cn = kwargs.pop('duplicate_cn', OpenvpnParser.duplicate_cn)
        super().__init__(*args, **kwargs)

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
        special_cases = self._find_special_cases(clients)
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
                'common_name': client.common_name,
            }
            local_addresses = [
                str(route.virtual_address)
                for route in data.routing_table.values()
                if route.real_address == address
            ]
            if local_addresses:
                client_properties['local_addresses'] = local_addresses
            node_id = self.get_node_id(client, special_cases)
            graph.add_node(node_id, **client_properties)
        # add links in routing table to graph
        for link in links:
            if link.common_name == 'UNDEF':
                continue
            target_id = self.get_target_id(link, special_cases)
            graph.add_edge(server, str(target_id), weight=1)
        return graph

    def get_node_id(self, client, special_cases):
        """
        when duplicate_cn is True
            if there are multiple nodes with the same common name
            and host address, add the port to the node ID
        when self.duplicate_cn is False:
            just use the common_name as node ID
        """
        if not self.duplicate_cn:
            return client.common_name
        address = client.real_address
        node_id = f'{client.common_name},{address.host}'
        if node_id in special_cases:
            node_id = f'{node_id}:{address.port}'
        return node_id

    def get_target_id(self, link, special_cases):
        """
        when duplicate_cn is True
            if there are multiple nodes with the same common name
            and host address, add the port to the target ID
        when self.duplicate_cn is False:
            just use the common_name as target ID
        """
        if not self.duplicate_cn:
            return link.common_name
        address = link.real_address
        target_id = f'{link.common_name},{address.host}'
        if target_id in special_cases:
            target_id = f'{target_id}:{address.port}'
        return target_id

    def _find_special_cases(self, clients):
        if not self.duplicate_cn:
            return []
        id_list = []
        special_cases = []
        for client in clients:
            id_ = f'{client.common_name},{client.real_address.host}'
            if id_ in id_list:
                special_cases.append(id_)
                continue
            id_list.append(id_)
        return special_cases
