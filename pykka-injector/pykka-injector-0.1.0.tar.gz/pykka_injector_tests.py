# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from injector import inject, Injector, InstanceProvider
from nose.tools import eq_
from pykka import ActorRegistry, ThreadingActor

from pykka_injector import ActorStarter


@inject(injected=str)
class Actor(ThreadingActor):
    pass


def test_starting_an_actor():
    def configure(binder):
        binder.bind(str, to=InstanceProvider('asd'))

    injector = Injector([configure])

    starter = injector.get(ActorStarter)
    actor_ref = starter.start(Actor)
    proxy = actor_ref.proxy()

    eq_(proxy.injected.get(), 'asd')


def teardown():
    ActorRegistry.stop_all()
