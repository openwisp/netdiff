class NetdiffException(Exception):
    """ root netdiff exception """
    pass


class ConversionException(NetdiffException):
    """
    netdiff can't recognize the format passed
    not necessarily an error, should be caught and managed
    in order to support additional formats

    The data which was retrieved from network/storage
    can be assecced via the "data" attribute
    """
    def __init__(self, *args, **kwargs):
        self.data = kwargs.pop('data')


class ParserError(NetdiffException):
    """
    the format is recognized but the data is invalid
    """
    pass


class NetJsonError(NetdiffException):
    """
    the json method of BaseParser does not have
    enough data to be compliant with the NetJSON spec
    """
    pass


class TopologyRetrievalError(NetdiffException):
    """
    it is not possible to retrieve the topology data
    (eg: the URL might be temporary unreachable)
    """
    pass
