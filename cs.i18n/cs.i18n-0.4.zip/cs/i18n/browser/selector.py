from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from plone.app.i18n.locales.browser.selector import LanguageSelector as LSBase

from zope.i18n.interfaces import IUserPreferredLanguages
from plone.memoize.view import memoize

class LanguageSelector(LSBase):
    render = ZopeTwoPageTemplateFile('templates/languageselector.pt')


    def languages(self):
        """ Returns list of languages """
        
        results = LSBase.languages(self)
        lang_info = self.tool.getAvailableLanguageInformation()

        for data in results:
            data['native'] = lang_info.get(data['code']).get(u'native', None).strip()

        return sorted(results, lambda x,y:cmp(x['native'],y['native']))

    @memoize
    def getPreferredLanguage(self):
        return IUserPreferredLanguages(self.request).getPreferredLanguages()[0]
