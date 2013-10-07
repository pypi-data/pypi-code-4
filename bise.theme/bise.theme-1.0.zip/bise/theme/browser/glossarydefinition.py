from .interfaces import IThemeSpecific
from Acquisition import aq_inner
from five import grok
from plone.app.contentlisting.interfaces import IContentListing
from plone.i18n.locales.interfaces import IMetadataLanguageAvailability
from plone.memoize.view import memoize
from Products.PloneGlossary.interfaces import IPloneGlossaryDefinition
from zope.component import getUtility


grok.templatedir('templates')


class GlossaryDefinitionView(grok.View):
    grok.context(IPloneGlossaryDefinition)
    grok.name('ploneglossarydefinition_view')
    grok.layer(IThemeSpecific)

    def sub_definitions(self):
        context = aq_inner(self.context)
        brains = context.getFolderContents(
            {'portal_type': 'PloneGlossaryDefinition'}
        )
        return IContentListing(brains)

    @memoize
    def get_language_dict(self):
        lang_utility = getUtility(IMetadataLanguageAvailability)
        return lang_utility.getLanguages(combined=True)

    def language_name(self, lang_code):
        lang = lang_code.lower().replace('_', '-')
        return self.get_language_dict().get(lang).get(u'name', lang)

    def term_translations(self):
        context = aq_inner(self.context)
        trans = context.getField('term_translations').get(context)
        return [{'term': t['term'], 'language': self.language_name(t['language'])} for t in trans]

    def definition_translations(self):
        context = aq_inner(self.context)
        trans = context.getField('definition_translations').get(context)
        return [{'definition': t['definition'], 'language': self.language_name(t['language'])} for t in trans]
