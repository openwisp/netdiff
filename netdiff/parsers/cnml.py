import os

import libcnml

from ..exceptions import ParserError
from .base import BaseParser

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


class CnmlParser(BaseParser):
    """ CNML 0.1 parser """

    protocol = 'static'
    version = None
    metric = None

    def to_python(self, data):
        if isinstance(data, str):
            up = urlparse.urlparse(data)
            # if it looks like a file path
            if os.path.isfile(data) or up.scheme in ['http', 'https']:
                return libcnml.CNMLParser(data)
            else:
                raise ParserError('Could not decode CNML data')
        elif isinstance(data, libcnml.CNMLParser):
            return data
        else:
            raise ParserError('Could not find valid data to parse')

    def parse(self, data):
        """
        Converts a CNML structure to a NetworkX Graph object
        which is then returned.
        """
        graph = self._init_graph()
        # loop over links and create networkx graph
        # Add only working nodes with working links
        for link in data.get_inner_links():
            if link.status != libcnml.libcnml.Status.WORKING:
                continue
            interface_a, interface_b = link.get_linked_interfaces()
            source = interface_a.ipv4
            dest = interface_b.ipv4
            # add link to Graph
            graph.add_edge(source, dest, weight=1)
        return graph
