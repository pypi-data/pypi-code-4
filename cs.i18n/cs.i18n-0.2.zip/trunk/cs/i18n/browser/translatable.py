from Products.LinguaPlone.browser.selector import TranslatableLanguageSelector as TLSBase

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from zope.i18n.interfaces import IUserPreferredLanguages

class TranslatableLanguageSelector(TLSBase):
    render = ZopeTwoPageTemplateFile('templates/translatablelanguageselector.pt')

    def languages(self):
        """ Return languages sorted according to their native name """
        results = TLSBase.languages(self)
        return sorted(results, lambda x,y:cmp(x['native'],y['native']))

