VERSION = (0, 1, 0, 'alpha')
__version__ = VERSION


def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3:] == ('alpha', 0):
        version = '%s pre-alpha' % version
    else:
        if VERSION[3] != 'final':
            version = '%s %s' % (version, VERSION[3])
    return version


from .parsers.olsr import OlsrParser  # noqa
from .parsers.batman import BatmanParser  # noqa
from .parsers.netjson import NetJsonParser  # noqa
from .utils import diff  # noqa
