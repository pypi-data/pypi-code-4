# -*- coding: utf-8 -*-
#
# File: __init__.py

__author__ = 'Ramon Bartl <ramon.bartl@nexiles.de>'
__docformat__ = 'plaintext'

import transaction
from thread import allocate_lock

from zope import interface
from zope import component

from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.filerepresentation.interfaces import IFileFactory

from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFPlone import utils as ploneutils
from Products.CMFCore import utils as cmfutils

from interfaces import IUploadingCapable

upload_lock = allocate_lock()


class UploadingCapableFileFactory(object):
    interface.implements(IFileFactory)
    component.adapts(IUploadingCapable)

    def __init__(self, context):
        self.context = context

    def __call__(self, name, content_type, data, obj_id):
        ctr = cmfutils.getToolByName(self.context, 'content_type_registry')
        type_ = ctr.findTypeName(name.lower(), '', '') or 'File'

        # otherwise I get ZPublisher.Conflict ConflictErrors
        # when uploading multiple files
        upload_lock.acquire()

        try:
            transaction.begin()
            obj = ploneutils._createObjectByType(type_, self.context, obj_id)
            mutator = obj.getPrimaryField().getMutator(obj)
            mutator(data, content_type=content_type)
            obj.setTitle(name)
            obj.reindexObject()

            notify(ObjectInitializedEvent(obj))
            notify(ObjectModifiedEvent(obj))

            transaction.commit()
        finally:
            upload_lock.release()
        return obj

# vim: set ft=python ts=4 sw=4 expandtab :
