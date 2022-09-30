from copy import deepcopy
from datetime import datetime, timedelta

from ..exceptions import ConversionException, ParserError
from .base import BaseParser


class WireguardParser(BaseParser):
    """wireguard parser"""

    protocol = 'Wireguard Status Log'
    version = '1'
    metric = 'static'
    max_time_diff = timedelta(minutes=5)

    def to_python(self, data):
        try:
            return super().to_python(data)
        except ConversionException as e:
            return self._wg_dump_to_python(e.data)

    def __parse_value(self, value):
        return None if value == '(none)' else value

    def _wg_dump_to_python(self, data):
        lines = map(lambda line: line.split('\t'), data.strip().split('\n'))
        try:
            parsed_lines = self._parse_lines(lines)
        except ValueError:
            raise ParserError('Unrecognized format')
        return parsed_lines

    def _parse_lines(self, lines):
        parsed_lines = {}
        last_device = None
        for device, *options in lines:
            if device != last_device:
                last_device = device
                _, public_key, listen_port, fwmark = map(self.__parse_value, options)
                parsed_lines.setdefault(
                    device,
                    dict(
                        public_key=public_key,
                        listen_port=listen_port,
                        fwmark=fwmark,
                        peers=[],
                    ),
                )
            else:
                (
                    public_key,
                    preshared_key,
                    endpoint,
                    allowed_ips,
                    latest_handshake,
                    transfer_rx,
                    transfer_tx,
                    persistent_keepalive,
                ) = map(self.__parse_value, options)
                connected, latest_handshake = self._parse_latest_handshake(
                    latest_handshake
                )
                parsed_lines[device]['peers'].append(
                    {
                        public_key: dict(
                            preshared_key=preshared_key,
                            endpoint=endpoint,
                            latest_handshake=latest_handshake.strftime(
                                '%Y-%m-%dT%H:%M:%SZ'
                            ),
                            transfer_rx=transfer_rx,
                            transfer_tx=transfer_tx,
                            persistent_keepalive=persistent_keepalive,
                            allowed_ips=allowed_ips.split(',') if allowed_ips else [],
                            connected=connected,
                        ),
                    }
                )
        return parsed_lines

    def _parse_latest_handshake(self, latest_handshake):
        """
        If the device hasn't handshaked for more than 5 minutes (by default)
        or if it has never handshaked (handshake is zero) we assume the device
        is not connected.
        """
        connection_time = datetime.fromtimestamp(int(latest_handshake))
        return (
            int(latest_handshake) != 0
            and datetime.now() - connection_time < self.max_time_diff,
            connection_time,
        )

    def parse(self, data):
        graph = self._init_graph()
        data = deepcopy(data)
        for interface, interface_properties in data.items():
            peers = interface_properties.pop('peers', [])
            graph.add_node(interface, **interface_properties)
            for peer in peers:
                public_key = (*peer,)[0]
                peer_properties = peer[public_key]
                if not peer_properties.get('connected'):
                    continue
                allowed_ips = ', '.join(peer_properties.get('allowed_ips', []))
                graph.add_node(public_key, label=allowed_ips, **peer_properties)
                graph.add_edge(public_key, interface, weight=1)
        return graph
