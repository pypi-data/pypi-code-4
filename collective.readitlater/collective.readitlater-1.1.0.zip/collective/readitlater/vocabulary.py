import json

from AccessControl import getSecurityManager
from plone.i18n.normalizer.base import baseNormalize
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from collective.readitlater.registry import IReaditlaterSettings


def contentVocabulary(context):
    sm = getSecurityManager()
    catalog = getToolByName(context, 'portal_catalog')
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IReaditlaterSettings)
    folder_query = json.loads(settings.folder_query)
    brains = catalog.searchResults(**folder_query)
    terms = []
    for brain in brains:
        if sm.checkPermission('Add portal content', brain.getObject()):
            terms.append(SimpleTerm(
                baseNormalize(brain.UID),
                baseNormalize(brain.UID),
                brain.Title.decode('utf-8')
            ))
    return SimpleVocabulary(terms)
