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

.. image:: https://img.shields.io/pypi/dm/netdiff.svg
   :target: https://pypi.python.org/pypi/netdiff

------------

Netdiff is an experimental Python library that provides utilities for parsing network topologies
of open source dynamic routing protocols and calculating changes in these topologies.

It was developed to abstract the differences between the different JSON structures of the
open source dynamic routing protocols (like **OLSR** and **batman-advanced**).

It's currently also used in `Nodeshot <https://github.com/ninuxorg/nodeshot>`__
to update the network links that are shown on the map.

If you are a developer of another community network node-db project and you want
to use netdiff to update the topology stored in your database, please
`get in touch <http://ml.ninux.org/mailman/listinfo/ninux-dev>`__!

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

    old = OlsrParser('./stored-olsr.json')
    new = OlsrParser('telnet://127.0.0.1:9090')
    diff(old, new)

In alternative, you may also use the subtraction operator:

.. code-block:: python

    from netdiff import OlsrParser
    from netdiff import diff

    old = OlsrParser('./stored-olsr.json')
    new = OlsrParser('telnet://127.0.0.1:9090')
    old - new

The output will be an ordered dictionary with three keys:

* added
* removed
* changed

Each key will contain a dict compatible with the `NetJSON NetworkGraph format <https://github.com/interop-dev/netjson#network-graph>`__
representing respectively:

* the nodes and links that have been added to the topology
* the nodes and links that have been removed from the topology
* links that are present in both topologies but their weight changed

If no changes are present, keys will contain ``None``.

So if between ``old`` and ``new`` there are no changes, the result will be:

.. code-block:: python

    {
        "added": None
        "removed": None,
        "changed": None
    }

While if there are changes, the result will look like:

.. code-block:: python

    {
        "added": {
            "type": "NetworkGraph",
            "protocol": "OLSR",
            "version": "0.6.6",
            "revision": "5031a799fcbe17f61d57e387bc3806de",
            "metric": "ETX",
            "nodes": [
                {
                    "id": "10.150.0.7"
                },
                {
                    "id": "10.150.0.6"
                }
            ],
            "links": [
                {
                    "source": "10.150.0.3",
                    "target": "10.150.0.7",
                    "weight": 1.50390625
                },
                {
                    "source": "10.150.0.3",
                    "target": "10.150.0.6",
                    "weight": 1.0
                }
            ]
        },
        "removed": {
            "type": "NetworkGraph",
            "protocol": "OLSR",
            "version": "0.6.6",
            "revision": "5031a799fcbe17f61d57e387bc3806de",
            "metric": "ETX",
            "nodes": [
                {
                    "id": "10.150.0.8"
                }
            ],
            "links": [
                {
                    "source": "10.150.0.7",
                    "target": "10.150.0.8",
                    "weight": 1.0
                }
            ]
        },
        "changed": {
            "type": "NetworkGraph",
            "protocol": "OLSR",
            "version": "0.6.6",
            "revision": "5031a799fcbe17f61d57e387bc3806de",
            "metric": "ETX",
            "nodes": [],
            "links": [
                {
                    "source": "10.150.0.3",
                    "target": "10.150.0.2",
                    "weight": 1.0
                }
            ]
        }
    }

Parsers
-------

Parsers are classes that extend ``netdiff.base.BaseParser`` and implement a ``parse`` method
which is in charge of converting a python data structure into ``networkx.Graph`` object.

Parsers also have a ``json`` method which returns valid `NetJSON output <https://github.com/ninuxorg/netdiff#netjson-output>`__.

The available parsers are:

* ``netdiff.OlsrParser``: parser for the `olsrd jsoninfo plugin <http://www.olsr.org/?q=jsoninfo_plugin>`__
* ``netdiff.BatmanParser``: parser for the `batman-advanced alfred tool <http://www.open-mesh.org/projects/open-mesh/wiki/Alfred>`__
* ``netdiff.Bmx6Parser``: parser for the BMX6 `b6m tool <http://dev.qmp.cat/projects/b6m>`__
* ``netdiff.CnmlParser``: parser for `CNML 0.1 <http://cnml.info/>`__
* ``netdiff.NetJsonParser``: parser for the ``NetworkGraph`` `NetJSON object <https://github.com/interop-dev/netjson#network-graph>`__.

Initialization arguments
~~~~~~~~~~~~~~~~~~~~~~~~

**data**: the only required argument, different inputs are accepted:

* JSON formatted string representing the topology
* python `dict` (or subclass of `dict`) representing the topology
* string representing a HTTP URL where the data resides
* string representing a telnet URL where the data resides
* string representing a file path where the data resides

**timeout**: integer representing timeout in seconds for HTTP or telnet requests, defaults to None

**verify**: boolean indicating to the `request library whether to do SSL certificate verification or not <http://docs.python-requests.org/en/latest/user/advanced/#ssl-cert-verification>`__

Initialization examples
~~~~~~~~~~~~~~~~~~~~~~~

Local file example:

.. code-block:: python

    from netdiff import BatmanParser
    BatmanParser('./my-stored-topology.json')

HTTP example:

.. code-block:: python

    from netdiff import NetJsonParser
    url = 'https://raw.githubusercontent.com/interop-dev/netjson/master/examples/network-graph.json'
    NetJsonParser(url)

Telnet example with ``timeout``:

.. code-block:: python

    from netdiff import OlsrParser
    OlsrParser('telnet://127.0.1:8080', timeout=5)

HTTPS example with self-signed SSL certificate using ``verify=False``:

.. code-block:: python

    from netdiff import NetJsonParser
    OlsrParser('https://myserver.mydomain.com/topology.json', verify=False)

NetJSON output
--------------

Netdiff parsers can return a valid `NetJSON <https://github.com/interop-dev/netjson>`__
``NetworkGraph`` object:

.. code-block:: python

    from netdiff import OlsrParser

    olsr = OlsrParser('telnet://127.0.0.1:9090')

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
                "weight": 2.4
            },
            {
                "source": "10.150.0.3",
                "target": "10.150.0.4",
                "weight": 1.0
            }
        ]
    }

Exceptions
----------

All the exceptions are subclasses of ``netdiff.exceptions.NetdiffException``.

ConversionException
~~~~~~~~~~~~~~~~~~~

``netdiff.exceptions.ConversionException``

Raised when netdiff can't recognize the format passed to the parser.

Not necessarily an error, should be caught and managed in order to support additional formats.

ParserError
~~~~~~~~~~~

``netdiff.exceptions.ParserError``

Raised when the format is recognized but the data is invalid.

NetJsonError
~~~~~~~~~~~~

``netdiff.exceptions.NetJsonError``

Raised when the ``json`` method of ``netdiff.parsers.BaseParser`` does not have enough data
to be compliant with the `NetJSON NetworkGraph <https://github.com/interop-dev/netjson#network-graph>`__ specification.

TopologyRetrievalError
~~~~~~~~~~~~~~~~~~~~~~

``netdiff.exceptions.TopologyRetrievalError``

Raised when it is not possible to retrieve the topology data
(eg: the URL might be temporary unreachable).

Running tests
-------------

Install your forked repo:

.. code-block:: shell

    git clone git://github.com/<your_fork>/netdiff
    cd netdiff/
    python setup.py develop

Install test requirements:

.. code-block:: shell

    pip install -r requirements-test.txt

Run tests with:

.. code-block:: shell

    ./runtests.py

Alternatively, you can use the ``nose`` command (which has a ton of available options):

.. code-block:: shell

    nosetests
    nosetests tests.test_olsr  # run only olsr related tests
    nosetests tests/test_olsr.py  # variant form of the previous command
    nosetests tests.test_olsr:TestOlsrParser  # variant form of the previous command
    nosetests tests.test_olsr:TestOlsrParser.test_parse  # run specific test

See test coverage with:

.. code-block:: shell

    coverage run --source=netdiff runtests.py && coverage report

Contributing
------------

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
