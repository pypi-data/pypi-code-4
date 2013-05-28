# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget
from plone.app.form.base import AddForm, EditForm
from plone.app.content.interfaces import INameFromTitle
from zope.formlib.form import applyChanges, Fields
from zope.component import createObject
from collective.cmisquery.content.cmisquery import ICMISQuery

from infrae.plone.relations.form import PloneRelationEditWidget
from infrae.plone.relations.form import PloneRelationSearchAddWidget
from zope.app.form import CustomWidgetFactory

widget_factory = CustomWidgetFactory(
    PloneRelationEditWidget,
    add_widget=PloneRelationSearchAddWidget,
    add_widget_args=dict(content_type='CMIS Browser'))


class CMISQueryAddForm(AddForm):
    label = u'Add a CMIS Query'
    form_fields = Fields(INameFromTitle, ICMISQuery)
    form_fields['browser'].custom_widget = widget_factory
    form_fields['text'].custom_widget = WYSIWYGWidget

    def create(self, data):
        query = createObject(u"collective.cmisquery.CMISQuery")
        content = self.context.add(query)
        # We need to add the content before editing it, in order to
        # have a working reference: we would get not yet overwise.
        applyChanges(content, self.form_fields, data)
        return content

    def add(self, content):
        self._finished_add = True
        return content



class CMISQueryEditForm(EditForm):
    label = u'Edit a CMIS Query'
    form_fields = Fields(ICMISQuery)
    form_fields['browser'].custom_widget = widget_factory
    form_fields['text'].custom_widget = WYSIWYGWidget
