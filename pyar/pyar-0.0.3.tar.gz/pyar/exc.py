#-*- coding: utf-8 -*-

__author__ = 'Jefurry <jefurry@qq.com>'

import traceback


class PyARError(Exception):
    """Generic error class."""

class ArgumentError(PyARError):
    """Raised when an invalid or conflicting function argument is supplied.

    This error generally corresponds to construction time state errors.

    """

class DnsStringNotFoundError(PyARError):
	"""Not Found DNS String for Connection to Database."""

class DialectNotFoundError(PyARError):
	"""Not Found Dialect."""

class DBError(PyARError):
	"""Database Error."""

class DBConnectionError(DBError):
	"""Database Connection Error."""

class DBTableNotExistsError(DBError):
	"""Table Not Exists."""

class DBOperationError(DBError):
	"""Database Operation Error."""
