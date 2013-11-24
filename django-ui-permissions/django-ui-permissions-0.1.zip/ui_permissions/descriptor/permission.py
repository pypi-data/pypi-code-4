# -*- coding: utf-8 -*-

"""Module containing Permission class."""

from .resource import Resource


class Permission(object):

    @classmethod
    def get_resource(cls, url_name):
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            try:
                if issubclass(attr, Resource) and url_name in attr._Settings.url:
                    return attr
            except TypeError:
                pass
