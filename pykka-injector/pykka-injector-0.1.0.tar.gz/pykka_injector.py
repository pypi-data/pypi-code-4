# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from injector import inject, Injector

__version__ = '0.1.0'


@inject(_injector=Injector)
class ActorStarter(object):
    def start(self, actor_class, kwargs=None):
        '''Start Pykka Actor.

        :param actor_class: actor to start
        :type actor_class: subclass of :class:`pykka.Actor`
        :param kwargs: keyword arguments to pass to actor's initializer
        :type kwargs: dict
        :rtype: :class:`pykka.ActorRef` for started actor
        '''
        kwargs = kwargs or {}

        def fun(*inner_kwargs):
            obj = self._injector.create_object(
                actor_class,
                additional_kwargs=inner_kwargs
            )
            return obj

        bound_start = actor_class.start
        try:
            start_func = bound_start.im_func
        except AttributeError:
            start_func = bound_start.__func__

        return start_func(fun, **kwargs)
