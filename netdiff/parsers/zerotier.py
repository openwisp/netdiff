from netdiff.parsers.base import BaseParser


class ZeroTierParser(BaseParser):
    version = '1'
    metric = 'static'
    protocol = 'ZeroTier Controller Peers'

    def to_python(self, data):
        return super().to_python(data)

    def parse(self, data):
        graph = self._init_graph()
        for peer in data:
            # In the ZeroTier architecture, a 'LEAF' refers to a device
            # that is a member of a ZeroTier virtual network.
            # Therefore, we can skip peers with roles other than 'LEAF'
            # or with latency -1 (indicating not reachable)
            if peer.get('role') != 'LEAF' or peer.get('latency') == -1:
                continue
            # Similar to zerotier-cli peers command (PATH)
            # We only select path that are active, preferred, and not expired
            for path in peer.get('paths'):
                if (
                    not path.get('expired')
                    and path.get('active')
                    and path.get('preferred')
                ):
                    peer_address = peer.get('address')
                    peer_properties = dict(
                        label=peer_address,
                        address=peer_address,
                        role=peer.get('role'),
                        version=peer.get('version'),
                        tunneled=peer.get('tunneled'),
                        isBonded=peer.get('isBonded'),
                    )
                    graph.add_node('controller', label='controller')
                    graph.add_node(peer_address, **peer_properties)
                    graph.add_edge(
                        'controller', peer_address, weight=peer.get('latency'), **path
                    )
        return graph
