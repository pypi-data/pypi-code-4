# -*- coding: utf-8 -*-

from zope.interface import Interface

class IBaseModel(Interface):
    def query(cls):
        """Return a query object for the model"""
