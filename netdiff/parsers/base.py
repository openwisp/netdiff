import json
import telnetlib

import networkx
import requests

from ..exceptions import ConversionException, TopologyRetrievalError
from ..utils import _netjson_networkgraph, diff

try:
    import urlparse
except ImportError:  # pragma: no cover
    import urllib.parse as urlparse  # pragma: no cover


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

    def __init__(
        self,
        data=None,
        url=None,
        file=None,
        version=None,
        revision=None,
        metric=None,
        timeout=None,
        verify=True,
        directed=False,
    ):  # noqa
        """
        Initializes a new Parser

        :param data: ``str`` or ``dict`` containing topology data
        :param url: HTTP URL to retrieve topology data
        :param file: path to file containing topology data
        :param version: routing protocol version
        :param revision: routing protocol revision
        :param metric: routing protocol metric
        :param timeout: timeout in seconds for HTTP or telnet requests
        :param verify: boolean (valid for HTTPS requests only)
        :param directed: whether the resulting graph should be directed
                         (undirected by default for backwards compatibility)
        """
        if version:
            self.version = version
        if revision:
            self.revision = revision
        if metric:
            self.metric = metric
        self.timeout = timeout
        self.verify = verify
        self.directed = directed
        if data is None and url is not None:
            data = self._get_url(url)
        elif data is None and file is not None:
            data = self._get_file(file)
        elif data is None and url is None and file is None:
            raise ValueError(
                'no topology data supplied, on of the following arguments'
                'must be supplied: data, url or file'
            )
        self.original_data = self.to_python(data)
        # avoid throwing NotImplementedError in tests
        if self.__class__ is not BaseParser:
            self.graph = self.parse(self.original_data)

    def _get_url(self, url):
        url = urlparse.urlparse(url)
        if url.scheme in ['http', 'https']:
            return self._get_http(url)
        if url.scheme == 'telnet':
            return self._get_telnet(url)

    def __sub__(self, other):
        return diff(other, self)

    def to_python(self, data):
        """
        Parses the input data and converts it into a Python data structure
        Input data might be:
            * a path which points to a JSON file
            * a URL which points to a JSON file
              (supported schemes: http, https, telnet)
            * a JSON formatted string
            * a dict representing a JSON structure
        """
        if isinstance(data, dict):
            return data
        elif isinstance(data, str):
            # assuming is JSON
            try:
                return json.loads(data)
            except ValueError:
                pass
        raise ConversionException('Could not recognize format', data=data)

    def _get_file(self, path):
        try:
            return open(path).read()
        except Exception as e:
            raise TopologyRetrievalError(e)

    def _get_http(self, url):
        try:
            response = requests.get(
                url.geturl(), verify=self.verify, timeout=self.timeout
            )
        except Exception as e:
            raise TopologyRetrievalError(e)
        if response.status_code != 200:
            msg = 'Expecting HTTP 200 ok, got {0}'.format(response.status_code)
            raise TopologyRetrievalError(msg)
        return response.content.decode()

    def _get_telnet(self, url):
        try:
            tn = telnetlib.Telnet(url.hostname, url.port, timeout=self.timeout)
        except Exception as e:
            raise TopologyRetrievalError(e)
        tn.write(("\r\n").encode('ascii'))
        data = tn.read_all().decode('ascii')
        tn.close()
        return data

    def _init_graph(self):
        return networkx.DiGraph() if self.directed else networkx.Graph()

    def parse(self, data):
        """
        Converts the original python data structure into a NetworkX Graph object
        Must be implemented by subclasses.
        Must return an instance of <networkx.Graph>
        """
        raise NotImplementedError()

    def json(self, dict=False, **kwargs):
        """
        Outputs NetJSON format
        """
        try:
            graph = self.graph
        except AttributeError:
            raise NotImplementedError()
        return _netjson_networkgraph(
            self.protocol,
            self.version,
            self.revision,
            self.metric,
            graph.nodes(data=True),
            graph.edges(data=True),
            dict,
            **kwargs
        )
