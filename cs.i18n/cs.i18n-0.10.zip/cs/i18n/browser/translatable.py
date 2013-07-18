try:
    from Products.LinguaPlone.browser.selector import TranslatableLanguageSelector as LSBase
except ImportError:
    from plone.app.i18n.locales.browser.selector import LanguageSelector as LSBase

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from zope.i18n.interfaces import IUserPreferredLanguages

class TranslatableLanguageSelector(LSBase):
    render = ZopeTwoPageTemplateFile('templates/translatablelanguageselector.pt')

    def languages(self):
        """ Return languages sorted according to their native name """
        results = LSBase.languages(self)
        return sorted(results, lambda x,y:cmp(x['native'],y['native']))

