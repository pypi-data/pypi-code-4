from zope.interface import (
    Interface,
    Attribute,
)

class IMongoDelegate(Interface):
    def __init__(host, dbname, colname):
        """initialize host, dbname, colname"""

    def _delegate(func_name, *query, **kwquery):
        """mognodb operation"""

    def db():
        """Return mongodb collection"""
