__all__ = ("SourceQueryException", "InvalidResponse", "SocketClosed")


class SourceQueryException(Exception):
    pass


class InvalidResponse(SourceQueryException):
    pass


class SocketClosed(SourceQueryException):
    pass
