Changelog
=========

Version 0.3 [unreleased]
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
