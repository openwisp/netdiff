#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import nose2
except ImportError:
    message = """nose2 package not installed, install test requirements with:

    pip install -r requirements-test.txt
    """
    raise ImportError(message)

if __name__ == "__main__":
    nose2.discover()
