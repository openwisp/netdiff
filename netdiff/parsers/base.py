import six
import json
import requests
import telnetlib
from collections import OrderedDict

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from ..exceptions import NetParserException, NetJsonException
from ..olsr_txtinfo import TopologyParser


class BaseParser(object):
    """
    Base Class for Parsers
    To create a parser, extend this class
    and implement a parse method
    """
    protocol = None
    version = None
    revision = None
    metric = None

    def __init__(self, data, version=None, revision=None, metric=None):
        """
        Initializes a new Parser

        :param data: JSON, dict, path to file or HTTP URL of topology
        :param version: routing protocol version
        :param revision: routing protocol revision
        :param metric: routing protocol metric
        """
        if version:
            self.version = version
        if revision:
            self.revision = revision
        if metric:
            self.metric = metric
        self.original_data = self._to_python(data)
        # avoid throwing NotImplementedError in tests
        if self.__class__ is not BaseParser:
            self.parse(self.original_data)

    def _to_python(self, data):
        """
        Private method which parses the input data and converts it into a Python data structure
        Input data might be:
            * a path which points to a JSON file
            * a URL which points to a JSON file
              (supported schemas: http, https, telnet)
            * a JSON formatted string
            * a dict representing a JSON structure
        """
        # string
        if isinstance(data, six.string_types):
            # if it looks like a file path
            if True in [data.startswith('./'), data.startswith('../'), data.startswith('/')]:
                data = open(data).read()
            # if it looks like a HTTP URL
            elif data.startswith('http'):
                data = requests.get(data, verify=False).content.decode()
            # if it looks like a telnet URL
            elif data.startswith('telnet'):
                up = urlparse.urlparse(data)
                telnet_host = up.hostname
                telnet_port = up.port
                tn = telnetlib.Telnet(telnet_host, telnet_port)
                tn.write(("\r\n").encode('ascii'))
                data = tn.read_all().decode('ascii')
                tn.close()
            # assuming is JSON
            try:
                return json.loads(data)
            except ValueError:
                # perhaps we have a txtinfo format?
                try:
                    tp = TopologyParser(data)
                    return tp.toDict()
                except (ValueError, AttributeError, IndexError):
                    raise NetParserException('Could not decode data')
        elif isinstance(data, dict):
            return data
        else:
            raise NetParserException('Could not find valid data to parse')

    def parse(self, data):
        """
        Converts the original python data structure into a NetworkX Graph object
        Must be implemented by subclasses.
        """
        raise NotImplementedError()

    def json(self, dict=False, **args):
        """
        Outputs NetJSON format
        """
        try:
            graph = self.graph
        except AttributeError:
            raise NotImplementedError()
        # netjson formatting check
        if self.protocol is None:
            raise NetJsonException('protocol cannot be None')
        if self.version is None:
            raise NetJsonException('version cannot be None')
        if self.metric is None:
            raise NetJsonException('metric cannot be None')
        # prepare lists
        nodes = [{'id': node} for node in graph.nodes()]
        links = []
        for link in graph.edges(data=True):
            links.append(OrderedDict((
                ('source', link[0]),
                ('target', link[1]),
                ('weight', link[2]['weight'])
            )))
        data = OrderedDict((
            ('type', 'NetworkGraph'),
            ('protocol', self.protocol),
            ('version', self.version),
            ('revision', self.revision),
            ('metric', self.metric),
            ('nodes', nodes),
            ('links', links)
        ))
        if dict:
            return data
        return json.dumps(data, **args)
