import os
import six
import networkx

from netdiff import OlsrParser
from netdiff import diff
from netdiff.exceptions import NetParserException
from netdiff.tests import TestCase


__all__ = ['TestOlsrParser']


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
links2 = '{0}/../static/olsr-2-links.json'.format(CURRENT_DIR)
links3 = '{0}/../static/olsr-3-links.json'.format(CURRENT_DIR)
links5 = '{0}/../static/olsr-5-links.json'.format(CURRENT_DIR)
links3metric = '{0}/../static/olsr-3-links-with-metric.json'.format(CURRENT_DIR)


class TestOlsrParser(TestCase):

    def test_parse(self):
        p = OlsrParser(links2)
        self.assertIsInstance(p.graph, networkx.Graph)

    def test_init(self):
        p = OlsrParser(links2, version='0.6.3', metric='ETC')
        self.assertEqual(p.version, '0.6.3')
        self.assertEqual(p.metric, 'ETC')

    def test_parse_exception(self):
        with self.assertRaises(NetParserException):
            OlsrParser('{ "test": "test" }')

    def test_parse_exception2(self):
        with self.assertRaises(NetParserException):
            OlsrParser('{ "topology": [{ "a": "a" }] }')

    def test_json_dict(self):
        p = OlsrParser(links2)
        data = p.json(dict=True)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['type'], 'NetworkGraph')
        self.assertEqual(data['protocol'], 'OLSR')
        self.assertEqual(data['version'], '0.6')
        self.assertEqual(data['metric'], 'ETX')
        self.assertIsInstance(data['nodes'], list)
        self.assertIsInstance(data['links'], list)
        self.assertEqual(len(data['nodes']), 3)
        self.assertEqual(len(data['links']), 2)

    def test_json_string(self):
        p = OlsrParser(links2)
        data = p.json()
        self.assertIsInstance(data, six.string_types)
        self.assertIn('NetworkGraph', data)
        self.assertIn('protocol', data)
        self.assertIn('version', data)
        self.assertIn('metric', data)
        self.assertIn('OLSR', data)
        self.assertIn('0.6', data)
        self.assertIn('ETX', data)
        self.assertIn('links', data)
        self.assertIn('nodes', data)

    def test_no_changes(self):
        old = OlsrParser(links2)
        new = OlsrParser(links2)
        result = diff(old, new)
        self.assertTrue(type(result) is dict)
        self.assertTrue(type(result['added']) is list)
        self.assertTrue(type(result['removed']) is list)
        # ensure there are no differences
        self.assertEqual(len(result['added']), 0)
        self.assertEqual(len(result['removed']), 0)

    def test_added_1_link(self):
        old = OlsrParser(links2)
        new = OlsrParser(links3)
        result = diff(old, new)
        # ensure there are no differences
        self.assertEqual(len(result['added']), 1)
        self.assertEqual(len(result['removed']), 0)
        # ensure 1 link added
        self.assertIn('10.150.0.5', result['added'][0])
        self.assertIn('10.150.0.4', result['added'][0])

    def test_removed_1_link(self):
        old = OlsrParser(links3)
        new = OlsrParser(links2)
        result = diff(old, new)
        self.assertTrue(type(result) is dict)
        self.assertTrue(type(result['added']) is list)
        self.assertTrue(type(result['removed']) is list)
        # ensure there are no differences
        self.assertEqual(len(result['added']), 0)
        self.assertEqual(len(result['removed']), 1)
        # ensure 1 link removed
        self.assertIn('10.150.0.5', result['removed'][0])
        self.assertIn('10.150.0.4', result['removed'][0])

    def test_simple_diff(self):
        old = OlsrParser(links3)
        new = OlsrParser(links5)
        result = diff(old, new)
        # ensure there are no differences
        self.assertEqual(len(result['added']), 3)
        self.assertEqual(len(result['removed']), 1)
        # ensure 3 links added
        self._test_expected_links(
            links=result['added'],
            expected_links=[
                ('10.150.0.3', '10.150.0.7'),
                ('10.150.0.3', '10.150.0.6'),
                ('10.150.0.7', '10.150.0.6'),
            ]
        )
        self._test_expected_links(
            links=result['removed'],
            expected_links=[('10.150.0.5', '10.150.0.4')]
        )

    def test_diff_metric(self):
        old = OlsrParser(links3)
        new = OlsrParser(links3metric)
        result = diff(old, new, cost=1)
        # The metric has changed so we have -1 and +1
        self.assertEqual(len(result['added']), 1)
        self.assertEqual(len(result['removed']), 1)

    def test_diff_metric_threshold(self):
        old = OlsrParser(links3)
        new = OlsrParser(links3metric)
        result = diff(old, new, cost=2)
        # The metric has changed but is inside of the threshold (2)
        # no changes
        self.assertEqual(len(result['added']), 0)
        self.assertEqual(len(result['removed']), 0)
