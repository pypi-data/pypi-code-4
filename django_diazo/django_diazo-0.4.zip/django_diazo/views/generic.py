from django.http import HttpResponse
from django.views.generic import View, RedirectView
#from django.views.generic.base import ContextMixin  # Django 1.5 only
from django_diazo.utils.dict2xml import dict2xml


class DiazoEnableThemeView(View):
    def dispatch(self, request, *args, **kwargs):
        if 'django_diazo_theme_enabled' in request.session:
            request.session.pop('django_diazo_theme_enabled')
        return super(DiazoEnableThemeView, self).dispatch(request, *args, **kwargs)


class DiazoDisableThemeView(View):
    def dispatch(self, request, *args, **kwargs):
        request.session['django_diazo_theme_enabled'] = False
        return super(DiazoDisableThemeView, self).dispatch(request, *args, **kwargs)


class DiazoEnableThemeRedirectView(DiazoEnableThemeView, RedirectView):
    pass


class DiazoDisableThemeRedirectView(DiazoDisableThemeView, RedirectView):
    pass


class ContextMixin(object):
    """
    Copied from Django 1.5.
    A default context mixin that passes the keyword arguments received by
    get_context_data as the template context.
    """

    def get_context_data(self, **kwargs):
        if 'view' not in kwargs:
            kwargs['view'] = self
        return kwargs


class DiazoGenericXmlHtmlResponse(ContextMixin, View):
    """
    Clased based view to output XML as Html. By default, id's and classes are attributes of the tags.
    It uses the context data that is defined by get_context_data() from ContextMixin.

    Example usage:

    class IndexView(DiazoGenericXmlHtmlResponse):
        def get_context_data(self, **kwargs):
            context = {
                'id': 'test',
                'class': 'test',
                'title': 'Title',
                'list': [1, 2, 3, 4, 5],
                'dict': {
                    'a': 'b'
                }
            }
            return dict(super(IndexView, self).get_context_data(**kwargs).items() + context.items())
    """
    def __init__(self):
        super(DiazoGenericXmlHtmlResponse, self).__init__()
        self._attributenames = ['id', 'class']

    @property
    def attributenames(self):
        return self._attributenames
    @attributenames.setter
    def attributenames(self, value):
        self._attributenames = value

    def dispatch(self, request, *args, **kwargs):
        """
        Invoke the initial handler but don't return the reponse, we create our own response.
        """
        ret = super(DiazoGenericXmlHtmlResponse, self).dispatch(request, *args, **kwargs)
        context = self.get_context_data(**kwargs)
        content = '<?xml version="1.0" encoding="UTF-8"?>' +\
                  dict2xml(context, 'context', attributenames=self.attributenames)
        return HttpResponse(content, content_type="text/html")
