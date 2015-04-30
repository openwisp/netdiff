netdiff
=======

.. image:: https://travis-ci.org/ninuxorg/netdiff.png
   :target: https://travis-ci.org/ninuxorg/netdiff

.. image:: https://coveralls.io/repos/ninuxorg/netdiff/badge.png
  :target: https://coveralls.io/r/ninuxorg/netdiff

.. image:: https://landscape.io/github/ninuxorg/netdiff/master/landscape.png
   :target: https://landscape.io/github/ninuxorg/netdiff/master
   :alt: Code Health

.. image:: https://requires.io/github/ninuxorg/netdiff/requirements.png?branch=master
   :target: https://requires.io/github/ninuxorg/netdiff/requirements/?branch=master
   :alt: Requirements Status

.. image:: https://badge.fury.io/py/netdiff.png
   :target: http://badge.fury.io/py/netdiff

.. image:: https://pypip.in/d/netdiff/badge.png
   :target: https://pypi.python.org/pypi/netdiff

------------

Python library that calculates a diff of a network topology.

Install
-------

Install via pip::

    pip install -e git+git://github.com/ninuxorg/netdiff#egg=netdiff

Usage
-----

Calculate diff of an OLSR 0.6.x topology::

    from netdiff import OlsrParser
    from netdiff import diff

    stored = OlsrParser('./stored-olsr.json')
    latest = OlsrParser('http://127.0.0.1:2006')
    diff(stored, latest)

The output will be a dictionary with the following structure::

    {
        "added": []
        "removed": []
    }

Running tests
-------------

Clone / fork repo::

    git clone git://github.com/ninuxorg/netdiff
    cd diff/

Install test requirements::

    pip install -r requirements-test.txt

Run tests with::

    nosetests

See test coverage with::

    nosetests --with-coverage --cover-package=netdiff

Contribute
----------

1. Join the `ninux-dev mailing list`_
2. Fork this repo
3. Follow `PEP8, Style Guide for Python Code`_
4. Write code
5. Write tests for your code
6. Ensure all tests pass
7. Ensure test coverage is not under 90%
8. Document your changes
9. Send pull request

.. _PEP8, Style Guide for Python Code: http://www.python.org/dev/peps/pep-0008/
.. _ninux-dev mailing list: http://ml.ninux.org/mailman/listinfo/ninux-dev
