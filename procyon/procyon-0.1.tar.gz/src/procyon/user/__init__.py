# -*- coding: utf-8 -*-

import venusian

from .api import *
from .model import UserModelMixin


def user_model(wrapped):
    def callback(context, name, ob):
        set_user_model(context.config.registry, ob)

    info = venusian.attach(wrapped, callback, category='procyon')

    return wrapped


def includeme(config):
    config.add_directive('set_user_model', '.directives.set_user_model')
    config.add_directive('set_default_user_model', '.directives.set_default_user_model')
    config.add_request_method(callable='.directives.get_user_model')
    config.scan('.event')
