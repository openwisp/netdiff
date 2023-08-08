import json
from copy import deepcopy

from netdiff.parsers.base import BaseParser


class ZeroTierParser(BaseParser):
    protocol = 'ZeroTier Peers Information'
    version = '1'
    metric = 'static'

    def to_python(self, data):
        if isinstance(data, list):
            return data
        return super().to_python(data)

    def parse(self, data):
        graph = self._init_graph()
        for peer in data:
            if peer.get('role') != 'LEAF':
                continue
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
