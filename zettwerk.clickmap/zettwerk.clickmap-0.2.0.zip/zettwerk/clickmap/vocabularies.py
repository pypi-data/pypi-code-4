try:
    #plone <4.1
    from zope.app.schema.vocabulary import IVocabularyFactory
except ImportError:
    #plone >4.1
    from zope.schema.interfaces import IVocabularyFactory

from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFPlone.utils import safe_unicode

class ListPagesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        catalog = getToolByName(context, 'portal_catalog', None)
        if catalog is None:
            return None

        ## all, but Plone Site objects
        content = catalog()

        items = [(c['UID'], '%s (%s)' %(c.getPath(), safe_unicode(c['Title']))) for c in content]
        items = [SimpleTerm(i[0], i[0], i[1]) for i in items]

        return SimpleVocabulary(items)
    
ListPagesVocabularyFactory = ListPagesVocabulary()
