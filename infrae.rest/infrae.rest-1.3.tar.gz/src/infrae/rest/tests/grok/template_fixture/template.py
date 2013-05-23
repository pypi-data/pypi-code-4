# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from OFS.Folder import Folder
from five import grok
from infrae.rest import RESTWithTemplate


class LocalStatic(grok.DirectoryResource):
    """Local static folder is registered by hand here.
    """
    grok.path('static')
    grok.name('infrae.rest.tests.grok.template_fixture')


class FormTemplate(RESTWithTemplate):
    grok.context(Folder)
    grok.name('form')

    def value(self):
        return '42'

    def GET(self):
        return self.template.render(self)


class WidgetTemplate(RESTWithTemplate):
    grok.adapts(FormTemplate, Folder)
    grok.name('widget')

    def value(self):
        return '51'

    def GET(self):
        return self.template.render(self)


# Let's use an inline template here
widgettemplate = grok.PageTemplate('<span tal:content="rest/value"></span>')
