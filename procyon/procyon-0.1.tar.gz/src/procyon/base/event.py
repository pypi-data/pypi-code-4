# -*- coding: utf-8 -*-

from pyramid.events import subscriber, ApplicationCreated

from . import model


@subscriber(ApplicationCreated)
def setup_model(event):
    registry = event.app.registry
    model.setup_model(registry.settings)
