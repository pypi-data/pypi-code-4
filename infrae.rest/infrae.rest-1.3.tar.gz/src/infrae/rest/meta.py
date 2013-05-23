# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from App.class_init import InitializeClass as initializeClass
from Products.Five.security import protectName

from five import grok
from grokcore.view.meta.views import TemplateGrokker
import martian

from infrae.rest.components import REST, ALLOWED_REST_METHODS
from infrae.rest.components import RESTWithTemplate


class RESTSecurityGrokker(martian.ClassGrokker):
    """Grok REST views.
    """
    martian.component(REST)
    martian.priority(100)
    martian.directive(grok.require, name='permission')

    def execute(self, factory, permission, config, **kw):
        """Register the REST component as a view on the IREST layer.
        """
        # Set name. The priority of the grokker must be higher than 0
        # to be call before the component is registered by
        # zeam.component.
        if not grok.name.bind().get(factory):
            grok.name.set(factory, factory.__name__.lower())

        if permission is None:
            permission = 'zope.Public'

        for method in ALLOWED_REST_METHODS:
            if hasattr(factory, method):
                config.action(
                    discriminator = ('five:protectName', factory, method),
                    callable = protectName,
                    args = (factory, method, permission))

        config.action(
            discriminator = ('five:initialize:class', factory),
            callable = initializeClass,
            args = (factory,))
        return True


class RESTWithTemplateGrokker(TemplateGrokker):
    martian.component(RESTWithTemplate)

    def has_render(self, factory):
        return False

    def has_no_render(self, factory):
        return False

