# -*- coding: utf-8 -*-

from .base import DBSession, BaseModel
from .user import UserModelMixin


def includeme(config):
    config.include(".base")
    config.include(".user")

    if hasattr(config, 'add_jinja2_search_path'):
        config.add_jinja2_search_path('procyon:templates')
