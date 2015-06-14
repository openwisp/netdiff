Changelog
=========

Version 0.4 [14-06-2015]
------------------------

- `#21 <https://github.com/ninuxorg/netdiff/issues/21>`_: **breaking change** made ``diff`` output consistent with NetJSON ``NetworkGraph``
- `#24 <https://github.com/ninuxorg/netdiff/issues/24>`_: add "changed" section to ``diff`` to show changes in weight
- `a6a161a <https://github.com/ninuxorg/netdiff/commit/a6a161a>`_: ``diff`` now returns an OrderedDict

Version 0.3.2 [03-06-2015]
--------------------------

- `#26 <https://github.com/ninuxorg/netdiff/issues/26>`_: renamed exceptions with "NetParser" prefix
- `#25 <https://github.com/ninuxorg/netdiff/issues/25>`_: raise Exception if topology file/URL not reachable
- `53e02cc <https://github.com/ninuxorg/netdiff/commit/53e02cc>`_: flagged ``to_python`` of ``BaseParser`` as public
- `48d2927 <https://github.com/ninuxorg/netdiff/commit/48d2927>`_: refactored exceptions, added explaination in README

Version 0.3.1 [22-05-2015]
--------------------------

- `c91e4e <https://github.com/ninuxorg/netdiff/commit/c91e4e48917c6503fc490e725da1574cb5c549fe>`_: corrected weight in ``OlsrParser``
- `#22 <https://github.com/ninuxorg/netdiff/pull/22>`_: added subtraction operator as a shortcut to diff function
- `be9f476 <https://github.com/ninuxorg/netdiff/commit/be9f476>`_: corrected ``MANIFEST.in`` to fix egg builds

Version 0.3 [15-05-2015]
------------------------

- `#18 <https://github.com/ninuxorg/netdiff/pull/18>`_: added CNML parser
- `#17 <https://github.com/ninuxorg/netdiff/pull/17>`_: added BMX6 (b6m tool) parser
- `#16 <https://github.com/ninuxorg/netdiff/pull/16>`_: added ``NetParserJsonException`` which is raised if no JSON object can be decoded in ``_to_python``
- `#14 <https://github.com/ninuxorg/netdiff/pull/14>`_: replaced ``startswith`` string method with ``urlparse`` module for URL scheme recognition

Version 0.2 [08-05-2015]
------------------------

- `#12 <https://github.com/ninuxorg/netdiff/pull/12>`_: Added support for telnet urls in ``BaseParser``

Version 0.1 [02-05-2015]
------------------------

- Added ``OlsrParser``
- Added ``BatmanParser``
- Added ``NetJsonParser``
- Added ``json`` method to ``BaseParser`` which returns valid NetJSON
- Added ``diff`` function
