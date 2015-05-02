import networkx

from .base import BaseParser
from ..exceptions import NetParserException


class OlsrParser(BaseParser):
    """ OLSR 0.6.x parser """
    protocol = 'OLSR'
    version = '0.6'
    metric = 'ETX'

    def parse(self, data):
        """
        Converts a dict representing an OLSR 0.6.x topology in a NetworkX Graph object.
        """
        graph = networkx.Graph()
        if 'topology' not in data:
            raise NetParserException('Parse error, "topology" key not found')
        # loop over topology section and create networkx graph
        for link in data["topology"]:
            try:
                source = link["lastHopIP"]
                dest = link["destinationIP"]
                cost = link["tcEdgeCost"]
            except KeyError as e:
                raise NetParserException('Parse error, "%s" key not found' % e)
            # add link to Graph
            graph.add_edge(source, dest, weight=cost)
        self.graph = graph
        # determine version and revision
        if 'config' in data:
            version_info = data['config']['olsrdVersion'].replace(' ', '').split('-')
            self.version = version_info[1]
            # try to get only the git hash
            if 'hash_' in version_info[-1]:
                version_info[-1] = version_info[-1].split('hash_')[-1]
            self.revision = version_info[-1]
