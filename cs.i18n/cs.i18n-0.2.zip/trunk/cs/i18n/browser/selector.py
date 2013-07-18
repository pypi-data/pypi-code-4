from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from plone.app.i18n.locales.browser.selector import LanguageSelector as LSBase

from zope.i18n.interfaces import IUserPreferredLanguages

class LanguageSelector(LSBase):
    render = ZopeTwoPageTemplateFile('templates/languageselector.pt')

    def languages(self):
        """ Return languages sorted according to their native name """
        results = LSBase.languages(self)
        return sorted(results, lambda x,y:cmp(x['native'],y['native']))        
            
