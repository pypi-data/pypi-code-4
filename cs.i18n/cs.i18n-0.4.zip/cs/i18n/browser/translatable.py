from Products.LinguaPlone.browser.selector import TranslatableLanguageSelector as TLSBase

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from zope.i18n.interfaces import IUserPreferredLanguages
from plone.memoize.view import memoize

class TranslatableLanguageSelector(TLSBase):
    render = ZopeTwoPageTemplateFile('templates/translatablelanguageselector.pt')
    def languages(self):
        """ Returns list of languages """
        results = TLSBase.languages(self)
        lang_info = self.tool.getAvailableLanguageInformation()

        for data in results:
            data['native'] = lang_info.get(data['code']).get(u'native', None).strip()

        return sorted(results, lambda x,y:cmp(x['native'],y['native']))

    @memoize
    def getPreferredLanguage(self):
        return IUserPreferredLanguages(self.request).getPreferredLanguages()[0]
