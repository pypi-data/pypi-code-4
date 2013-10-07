from .interfaces import IThemeSpecific
from Acquisition import aq_inner
from five import grok
from plone.app.contentlisting.interfaces import IContentListing
from Products.PloneGlossary.interfaces import IPloneGlossary


grok.templatedir('templates')


class GlossaryView(grok.View):
    grok.context(IPloneGlossary)
    grok.name('ploneglossary_view')
    grok.layer(IThemeSpecific)

    def definitions(self):
        context = aq_inner(self.context)
        brains = context.getFolderContents(
            {'portal_type': 'PloneGlossaryDefinition'}
        )
        return IContentListing(brains)