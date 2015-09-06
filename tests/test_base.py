import os
import unittest
import responses

from netdiff import get_version
from netdiff.parsers.base import BaseParser
from netdiff.exceptions import ParserError, ConversionException, TopologyRetrievalError


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
