from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from plone.app.i18n.locales.browser.selector import LanguageSelector as LSBase

class LanguageSelector(LSBase):
    render = ZopeTwoPageTemplateFile('templates/languageselector.pt')


    def languages(self):
        """ Returns list of languages """

        results = LSBase.languages(self)
        lang_info = self.tool.getAvailableLanguageInformation()

        for data in results:
            data['native'] = lang_info.get(data['code']).get(u'native', None)

        return results
