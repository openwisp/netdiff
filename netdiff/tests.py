import unittest


__all__ = ['TestCase']


class TestCase(unittest.TestCase):
    """ netdiff TestCase """
    def _test_expected_links(self, links, expected_links):
        """
        Ensures the contents of links is the same of expected_links,
        indipendently from the ordering
        links and expected_links should be list of tuples.
        """
        found = 0
        # loop over all links (the result got by netdiff)
        for link in links:
            # all expected links must be in links
            for expected_link in expected_links:
                # use sets to ignore ordering
                if set(link) == set(expected_link):
                    found += 1
        self.assertEqual(found, len(expected_links))
