# -*- coding: utf-8 -*-

from .interfaces import IBaseModel
from .model import BaseModel, DBSession


def get_base_model(registry):
    return registry.queryUtility(IBaseModel, BaseModel)


def set_base_model(registry, base):
    registry.registerUtility(base, IBaseModel)


def includeme(config):
    config.scan('.event')
