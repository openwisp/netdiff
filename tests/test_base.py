import os
import unittest
import responses
import telnetlib
from requests.exceptions import ConnectionError
try:
    from unittest import mock
except ImportError:
    import mock

from netdiff import get_version
from netdiff.utils import _netjson_networkgraph
from netdiff.parsers.base import BaseParser
from netdiff.exceptions import (ParserError,
                                ConversionException,
                                TopologyRetrievalError,
                                NetJsonError)


class TestBaseParser(unittest.TestCase):
    """ BaseParser tests """

    def _load_contents(self, file):
        return open(os.path.abspath(file)).read()

    def test_version(self):
        get_version()

    def test_parse_file(self):
        dir = os.path.dirname(os.path.realpath(__file__))
        path = '{0}/static/olsr-2-links.json'.format(dir)
        p = BaseParser(path)
        self.assertIsInstance(p.original_data, dict)
        with self.assertRaises(TopologyRetrievalError):
            BaseParser('../wrong.json')

    @responses.activate
    def test_parse_http(self):
        responses.add(
            responses.GET,
            'http://localhost:9090',
            body=self._load_contents('tests/static/olsr-2-links.json')
        )
        p = BaseParser('http://localhost:9090')
        self.assertIsInstance(p.original_data, dict)

    @responses.activate
    def test_topology_retrieval_error_http_404(self):
        responses.add(
            responses.GET,
            'http://404.com',
            body='not found',
            status=404
        )
        with self.assertRaises(TopologyRetrievalError):
            BaseParser('http://404.com')

    @responses.activate
    def test_topology_retrieval_error_http(self):
        def request_callback(request):
            raise ConnectionError('test exception')
        responses.add_callback(
            responses.GET,
            'http://connectionerror.com',
            callback=request_callback,
        )
        with self.assertRaises(TopologyRetrievalError):
            BaseParser('http://connectionerror.com')

    @mock.patch('telnetlib.Telnet')
    def test_telnet_retrieval_error(self, MockClass):
        telnetlib.Telnet.side_effect=ValueError('testing exception')
        with self.assertRaises(TopologyRetrievalError):
            BaseParser('telnet://wrong.com')

    @mock.patch('telnetlib.Telnet')
    def test_telnet_retrieval(self, MockClass):
        with self.assertRaises(ConversionException):
            BaseParser('telnet://127.0.0.1')

    def test_topology_retrieval_error_file(self):
        with self.assertRaises(TopologyRetrievalError):
            BaseParser('./tests/static/wrong.json')

    def test_parse_json_string(self):
        p = BaseParser('{}')
        self.assertIsInstance(p.original_data, dict)
        p = BaseParser(u'{}')
        self.assertIsInstance(p.original_data, dict)

    def test_parse_dict(self):
        p = BaseParser({})
        self.assertIsInstance(p.original_data, dict)

    def test_parse_conversion_exception(self):
        with self.assertRaises(ConversionException):
            BaseParser('wrong [] ; .')

    def test_parse_error(self):
        with self.assertRaises(ConversionException):
            BaseParser(8)

    def test_parse_not_implemented(self):
        class MyParser(BaseParser):
            pass
        with self.assertRaises(NotImplementedError):
            MyParser('{}')

    def test_json_not_implemented(self):
        p = BaseParser('{}')
        with self.assertRaises(NotImplementedError):
            p.json()

    def test_netjson_networkgraph_func(self):
        with self.assertRaises(NetJsonError):
            _netjson_networkgraph(None, None, None, None, [], [])
        with self.assertRaises(NetJsonError):
            _netjson_networkgraph('bgp', None, None, None, [], [])
        with self.assertRaises(NetJsonError):
            _netjson_networkgraph('olsr', '2', None, None, [], [])
