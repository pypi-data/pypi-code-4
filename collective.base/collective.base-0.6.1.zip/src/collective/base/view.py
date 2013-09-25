from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.base.interfaces import IBaseFormView
from collective.base.interfaces import IBaseView
from zope.interface import implements


class BaseView(BrowserView):
    """Base view"""
    implements(IBaseView)
    template = ViewPageTemplateFile('views/base.pt')

    title = None
    description = None

    def __call__(self):
        self.request.set('disable_border', True)


class BaseFormView(BaseView):
    """Base view for base form"""

    implements(IBaseFormView)
    template = ViewPageTemplateFile('views/base-form.pt')
