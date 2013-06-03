################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

from zope.component import getUtility
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

def InstitutionVocabulary(context):
    """ Return all institutions as vocabulary """

    site = getUtility(ISiteRoot)
    catalog = getToolByName(site, 'portal_catalog')
    terms = list()
    for brain in catalog(portal_type='Institution', sort_on='sortable_title'):
        terms.append(SimpleTerm(value=brain.UID,
                                token=brain.UID,
                                title=brain.Title))
    return SimpleVocabulary(terms)
