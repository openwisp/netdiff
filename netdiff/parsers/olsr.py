import networkx

from .base import BaseParser
from ..exceptions import ParserError, ConversionException


class OlsrParser(BaseParser):
    """ OLSR 1 jsoninfo parser """
    protocol = 'OLSR'
    version = '0.8'
    metric = 'ETX'

    def to_python(self, data):
        """
        Adds support for txtinfo format
        """
        try:
            return super(OlsrParser, self).to_python(data)
        except ConversionException as e:
            return self._txtinfo_to_jsoninfo(e.data)

    def parse(self, data):
        """
        Converts a dict representing an OLSR 0.6.x topology
        to a NetworkX Graph object, which is then returned.
        Additionally checks for "config" data in order to determine version and revision.
        """
        graph = networkx.Graph()
        if 'topology' not in data:
            raise ParserError('Parse error, "topology" key not found')

        # determine version and revision
        if 'config' in data:
            version_info = data['config']['olsrdVersion'].replace(' ', '').split('-')
            self.version = version_info[1]
            # try to get only the git hash
            if 'hash_' in version_info[-1]:
                version_info[-1] = version_info[-1].split('hash_')[-1]
            self.revision = version_info[-1]

        # loop over topology section and create networkx graph
        for link in data["topology"]:
            try:
                source = link["lastHopIP"]
                dest = link["destinationIP"]
                cost = link["tcEdgeCost"]
            except KeyError as e:
                raise ParserError('Parse error, "%s" key not found' % e)
            # skip links with infinite cost
            if cost == float('inf'):
                continue
            # original olsrd cost (jsoninfo multiplies by 1024)
            cost = float(cost) / 1024.0
            # add link to Graph
            graph.add_edge(source, dest, weight=cost)
        return graph

    def _txtinfo_to_jsoninfo(self, data):
        """
        converts olsr 1 txtinfo format to jsoninfo
        """
        # replace INFINITE with inf, which is convertible to float
        data = data.replace('INFINITE', 'inf')
        # find interesting section
        lines = data.split('\n')

        try:
            start = lines.index('Table: Topology') + 2
            end = lines[start:].index('') + start
        except ValueError as e:
            raise ParserError(e)

        topology_lines = lines[start:end]
        # convert interesting section to jsoninfo format
        parsed_lines = []
        for line in topology_lines:
            values = line.split('\t')
            parsed_lines.append({
                "destinationIP": values[0],
                "lastHopIP": values[1],
                "linkQuality": float(values[2]),
                "neighborLinkQuality": float(values[3]),
                "tcEdgeCost": float(values[4]) * 1024.0
            })
        return {'topology': parsed_lines}
