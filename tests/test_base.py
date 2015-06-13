import os
import unittest

from netdiff import get_version
from netdiff.parsers.base import BaseParser
from netdiff.exceptions import ParserError, ConversionException, TopologyRetrievalError


__all__ = ['TestBaseParser']


class TestBaseParser(unittest.TestCase):
    """ BaseParser tests """

    def test_version(self):
        get_version()

    def test_parse_file(self):
        dir = os.path.dirname(os.path.realpath(__file__))
        path = '{0}/static/olsr-2-links.json'.format(dir)
        p = BaseParser(path)
        self.assertIsInstance(p.original_data, dict)
        with self.assertRaises(TopologyRetrievalError):
            BaseParser('../wrong.json')

    def test_parse_http(self):
        url = 'http://raw.githubusercontent.com/ninuxorg/netdiff/e7b677fca3f16a4365e1fd5a6a81e1039abedce5/tests/olsr1/2links.json'
        p = BaseParser(url)
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
