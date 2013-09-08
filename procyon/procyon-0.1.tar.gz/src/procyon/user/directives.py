# -*- coding: utf-8 -*-

from . import api


def set_user_model(config, user_model):
    user_model = config.maybe_dotted(user_model)
    api.set_user_model(config.registry, user_model)


def set_default_user_model(config, user_tablename='user'):
    api.set_default_user_model(config.registry, user_tablename)


def get_user_model(request):
    return api.get_user_model(request.registry)
