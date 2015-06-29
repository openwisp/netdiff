import networkx

from .base import BaseParser
from ..exceptions import ParserError, ConversionException


class BatmanParser(BaseParser):
    """ batman-adv parser """
    protocol = 'batman-adv'
    version = '2015.0'
    metric = 'TQ'

    # the default expected format
    _format = 'alfred_vis'

    def to_python(self, data):
        """
        Adds support for txtinfo format
        """
        try:
            return super(BatmanParser, self).to_python(data)
        except ConversionException as e:
            return self._txtinfo_to_python(e.data)

    def _txtinfo_to_python(self, data):
        """
        Converts txtinfo format to python
        """
        self._format = 'txtinfo'
        # find interesting section
        lines = data.split('\n')
        try:
            start = lines.index('Table: Topology') + 2
        except ValueError as e:
            raise ParserError(e)
        topology_lines = [line for line in lines[start:] if line]
        # convert to python list
        parsed_lines = []
        for line in topology_lines:
            values = line.split(' ')
            parsed_lines.append({
                'source': values[0],
                'target': values[1],
                'weight': float(values[4])
            })
        return parsed_lines

    def _get_primary(self, mac, collection):
        # Use the ag_node structure to return the main mac address associated to
        # a secondary mac, if none return itself.
        for node in collection:
            for interface in node:
                if mac == interface:
                    return node[0]
        return 0

    def _get_ag_node_list(self, data):
        # Create a structure of main and secondary mac address.
        ag_nodes = []
        for node in data:
            ag_interfaces = []
            ag_interfaces.append(node['primary'])
            if('secondary'in node):
                for interface in node['secondary']:
                    ag_interfaces.append(interface)
            ag_nodes.append(ag_interfaces)
        return ag_nodes

    def parse(self, data):
        """
        Calls the right method depending on the format,
        which can be one of the wollowing:
            * alfred_vis
            * txtinfo
        """
        method = getattr(self, '_parse_{0}'.format(self._format))
        method(data)

    def _parse_alfred_vis(self, data):
        """
        Converts a alfred-vis JSON object to a NetworkX Graph object.
        """
        # initialize graph and list of aggregated nodes
        graph = networkx.Graph()
        if 'source_version' in data:
            self.version = data['source_version']
        if 'vis' not in data:
            raise ParserError('Parse error, "vis" key not found')
        ag_nodes = self._get_ag_node_list(data['vis'])
        # loop over topology section and create networkx graph
        for node in data["vis"]:
            for neigh in node["neighbors"]:
                p_neigh = self._get_primary(neigh['neighbor'], ag_nodes)
                # networkx automatically ignores duplicated edges
                graph.add_edge(node['primary'], p_neigh, weight=neigh['metric'])
        self.graph = graph

    def _parse_txtinfo(self, data):
        """
        Converts the python list returned by self._txtinfo_to_python()
        to a NetworkX Graph object.
        """
        graph = networkx.Graph()
        for link in data:
            graph.add_edge(link['source'],
                           link['target'],
                           weight=link['weight'])
        self.graph = graph
