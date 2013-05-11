# -*- coding: utf-8 -*-
#
# File: dexterity.py

__author__ = 'Philip Bauer <bauer@starzel.de>'
__docformat__ = 'plaintext'

from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore import utils as cmfutils
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils as ploneutils
from plone.namedfile.file import NamedFile
from plone.namedfile.file import NamedImage
from plone.namedfile.interfaces import INamedFileField
from plone.namedfile.interfaces import INamedImageField
from plone.rfc822.interfaces import IPrimaryField
from thread import allocate_lock
from zope import component
from zope import interface
from zope.event import notify
from zope.filerepresentation.interfaces import IFileFactory
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema import getFieldsInOrder

from interfaces import IUploadingCapable

import transaction
import logging

try:
    from plone.namedfile.interfaces import INamedBlobFileField, INamedBlobImageField
    from plone.namedfile.file import NamedBlobFile, NamedBlobImage
    HAVE_BLOBS = True
except:
    HAVE_BLOBS = False

logger = logging.getLogger("collective.uploadify")
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

            ttool = getToolByName(self.context, 'portal_types')
            ctype = ttool[obj.portal_type]
            schema = ctype.lookupSchema()
            fields = getFieldsInOrder(schema)
            file_fields = [field for safe_name, field in fields
                           if INamedFileField.providedBy(field)
                           or INamedImageField.providedBy(field)]
            if len(file_fields) == 0:
                logger.info("An error happens : the dexterity content type %s "
                            "has no file field, rawdata can't be created",
                            obj.absolute_url())
            for file_field in file_fields:
                if IPrimaryField.providedBy(file_field):
                    break
            else:
                # Primary field can't be set ttw,
                # then, we take the first one
                file_field = file_fields[0]

            # TODO: use adapters
            if HAVE_BLOBS and INamedBlobImageField.providedBy(file_field):
                value = NamedBlobImage(data=data.read(), contentType=content_type,
                                       filename=unicode(obj_id, 'utf-8'))
            elif HAVE_BLOBS and INamedBlobFileField.providedBy(file_field):
                value = NamedBlobFile(data=data.read(), contentType=content_type,
                                      filename=unicode(obj_id, 'utf-8'))
            elif INamedImageField.providedBy(file_field):
                value = NamedImage(data=data.read(), contentType=content_type,
                                   filename=unicode(obj_id, 'utf-8'))
            elif INamedFileField.providedBy(file_field):
                value = NamedFile(data=data.read(), contentType=content_type,
                                  filename=unicode(obj_id, 'utf-8'))

            file_field.set(obj, value)
            obj.title = name
            obj.reindexObject()

            notify(ObjectInitializedEvent(obj))
            notify(ObjectModifiedEvent(obj))

            transaction.commit()
        finally:
            upload_lock.release()
        return obj
