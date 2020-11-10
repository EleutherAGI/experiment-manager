class WarrantException(Exception):
    """Base class for all Request exceptions"""


class NoAuthException(WarrantException):
    """Raised when no attached auth"""


class TimeOutException(WarrantException):
    """Raised when request times out"""


class TooManyRedirectsException(WarrantException):
    """Raised when request gets redirected too many times"""


class GenericRequestException(WarrantException):
    """Raised with general request exception"""
