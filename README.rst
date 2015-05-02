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

Netdiff is an experimental Python library that provides utilities for parsing network topologies
of open source dynamic routing protocols and calculating changes in these topologies.

It was developed to abstract the differences between the different JSON structures of the
open source dynamic routing protocols (like **OLSR** and **batman-advanced**).

Install stable version from pypi
--------------------------------

Install from pypi:

.. code-block:: shell

    pip install netdiff

Install development version
---------------------------

Install tarball:

.. code-block:: shell

    pip install https://github.com/ninuxorg/netdiff/tarball/master

Alternatively you can install via pip using git:

.. code-block:: shell

    pip install -e git+git://github.com/ninuxorg/netdiff#egg=netdiff

If you want to contribute, install your cloned fork:

.. code-block:: shell

    git clone git@github.com:<your_fork>/netdiff.git
    cd netdiff
    python setup.py develop

Basic Usage Example
-------------------

Calculate diff of an OLSR 0.6.x topology:

.. code-block:: python

    from netdiff import OlsrParser
    from netdiff import diff

    stored = OlsrParser('./stored-olsr.json')
    latest = OlsrParser('http://127.0.0.1:2006')
    diff(stored, latest)

The output will be a dictionary with the following structure:

.. code-block:: python

    {
        "added": []
        "removed": []
    }

NetJSON output
--------------

Netdiff parsers can return a valid `NetJSON <https://github.com/interop-dev/json-for-networks>`__
``NetworkGraph`` object:

.. code-block:: python

    from netdiff import OlsrParser

    olsr = OlsrParser('http://127.0.0.1:2006')

    # will return a dict
    olsr.json(dict=True)

    # will return a JSON formatted string
    print(olsr.json(indent=4))

Output:

.. code-block:: javascript

    {
        "type": "NetworkGraph",
        "protocol": "OLSR",
        "version": "0.6.6",
        "revision": "5031a799fcbe17f61d57e387bc3806de",
        "metric": "ETX",
        "nodes": [
            {
                "id": "10.150.0.3"
            },
            {
                "id": "10.150.0.2"
            },
            {
                "id": "10.150.0.4"
            }
        ],
        "links": [
            {
                "source": "10.150.0.3",
                "target": "10.150.0.2",
                "weight": 28334
            },
            {
                "source": "10.150.0.3",
                "target": "10.150.0.4",
                "weight": 1024
            }
        ]
    }


Parsers
-------

Parsers are classes that extend ``netdiff.base.BaseParser`` and implement a ``parse`` method
which is in charge of converting a python data structure into ``networkx.Graph`` object.

Parsers have a ``json`` method which returns ``NetJSON``.

Running tests
-------------

Clone / fork repo:

.. code-block:: shell

    git clone git://github.com/ninuxorg/netdiff
    cd diff/

Install test requirements:

.. code-block:: shell

    pip install -r requirements-test.txt

Run tests with:

.. code-block:: shell

    ./runtests.py

Alternatively, you can use the ``nose`` command (which has a ton of available options):

.. code-block:: shell

    nosetests

See test coverage with:

.. code-block:: shell

    coverage run --source=netdiff runtests.py && coverage report

Contribute
----------

1. Join the `ninux-dev mailing list`_
2. Fork this repo and install it
3. Follow `PEP8, Style Guide for Python Code`_
4. Write code
5. Write tests for your code
6. Ensure all tests pass
7. Ensure test coverage is not under 90%
8. Document your changes
9. Send pull request

.. _PEP8, Style Guide for Python Code: http://www.python.org/dev/peps/pep-0008/
.. _ninux-dev mailing list: http://ml.ninux.org/mailman/listinfo/ninux-dev
