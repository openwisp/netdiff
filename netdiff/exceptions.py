class NetdiffException(Exception):
    pass


class ParserError(NetdiffException):
    pass


class ParserJsonError(NetdiffException):
    pass


class NetJsonError(NetdiffException):
    pass
