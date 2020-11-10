class WarrantException(Exception):
    """Base class for all Storage exceptions"""


class NoAuthException(WarrantException):
    """Raised when no attached auth"""
