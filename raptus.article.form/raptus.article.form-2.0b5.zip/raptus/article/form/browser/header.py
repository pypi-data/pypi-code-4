from zope import interface, component

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from raptus.article.form.interfaces import IForms as IFormsProvider
from raptus.article.form.browser.forms import IForms

class Viewlet(ViewletBase):
    """ Viewlet including the necessary javascript and css files for the forms
    """
    index = ViewPageTemplateFile('header.pt')
    
    @property
    def forms(self):
        provider = IFormsProvider(self.context)
        forms = provider.getForms()
        return [form.getObject() for form in forms]
    