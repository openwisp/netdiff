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
        except ValueError:
            raise ParserError('Unrecognized format')
        topology_lines = [line for line in lines[start:] if line]
        # convert to python list
        parsed_lines = []
        for line in topology_lines:
            values = line.split(' ')
            parsed_lines.append({
                'source': values[0],
                'target': values[1],
                'cost': float(values[4])
            })
        return parsed_lines

    def _get_primary_address(self, mac_address, node_list):
        """
        Uses the _get_aggregated_node_list structure to find
        the primary mac address associated to a secondary one,
        if none is found returns itself.
        """
        for local_addresses in node_list:
            if mac_address in local_addresses:
                return local_addresses[0]
        # remote case
        raise ValueError('primary address not found')

    def _get_aggregated_node_list(self, data):
        """
        Returns list of main and secondary mac addresses.
        """
        node_list = []
        for node in data:
            local_addresses = [node['primary']]
            if 'secondary' in node:
                local_addresses += node['secondary']
            node_list.append(local_addresses)
        return node_list

    def parse(self, data):
        """
        Calls the right method depending on the format,
        which can be one of the wollowing:
            * alfred_vis
            * txtinfo
        """
        method = getattr(self, '_parse_{0}'.format(self._format))
        return method(data)

    def _parse_alfred_vis(self, data):
        """
        Converts a alfred-vis JSON object
        to a NetworkX Graph object which is then returned.
        Additionally checks for "source_vesion" to determine the batman-adv version.
        """
        # initialize graph and list of aggregated nodes
        graph = networkx.Graph()
        if 'source_version' in data:
            self.version = data['source_version']
        if 'vis' not in data:
            raise ParserError('Parse error, "vis" key not found')
        node_list = self._get_aggregated_node_list(data['vis'])

        # loop over topology section and create networkx graph
        for node in data["vis"]:
            for neigh in node["neighbors"]:
                graph.add_node(node['primary'], **{
                    'local_addresses': node.get('secondary', []),
                    'clients': node.get('clients', [])
                })
                primary_neigh = self._get_primary_address(neigh['neighbor'],
                                                          node_list)
                # networkx automatically ignores duplicated edges
                graph.add_edge(node['primary'],
                               primary_neigh,
                               weight=float(neigh['metric']))
        return graph

    def _parse_txtinfo(self, data):
        """
        Converts the python list returned by self._txtinfo_to_python()
        to a NetworkX Graph object, which is then returned.
        """
        graph = networkx.Graph()
        for link in data:
            graph.add_edge(link['source'],
                           link['target'],
                           weight=link['cost'])
        return graph
