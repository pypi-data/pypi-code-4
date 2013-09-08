# -*- coding: utf-8 -*-

from zope.interface import provider

from procyon.base import get_base_model
from .interfaces import IUserModel
from .model import UserModelMixin

__all__ = [
    'create_user_model',
    'get_user_model',
    'set_user_model',
    'set_default_user_model',
]

def create_user_model(registry, user_tablename='user'):
    base = get_base_model(registry)

    @provider(IUserModel)
    class UserModel(UserModelMixin, base):
        __tablename__ = user_tablename

    return UserModel


def get_user_model(registry):
    return registry.queryUtility(IUserModel)


def set_user_model(registry, user_model):
    registry.registerUtility(user_model, IUserModel)


def set_default_user_model(registry, user_tablename='user'):
    user_model = create_user_model(registry)
    set_user_model(registry, user_model)
