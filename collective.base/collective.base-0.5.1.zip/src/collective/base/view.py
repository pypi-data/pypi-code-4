from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.base.interfaces import IBaseFormView
from zope.interface import implements


class BaseFormView(BrowserView):
    """Base view for base form"""

    implements(IBaseFormView)
    template = ViewPageTemplateFile('templates/base-form.pt')

    title = None
    description = None

    def __call__(self):
        self.request.set('disable_border', True)
