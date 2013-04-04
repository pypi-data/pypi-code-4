from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Model
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import authenticate
from django.template import TemplateDoesNotExist, RequestContext, loader

from social.strategies.base import BaseStrategy, BaseTemplateStrategy


class DjangoTemplateStrategy(BaseTemplateStrategy):
    def render_template(self, tpl, context):
        template = loader.get_template(tpl)
        return template.render(RequestContext(self.strategy.request, context))

    def render_string(self, html, context):
        template = loader.get_template_from_string(html)
        return template.render(RequestContext(self.strategy.request, context))


class DjangoStrategy(BaseStrategy):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('tpl', DjangoTemplateStrategy)
        super(DjangoStrategy, self).__init__(*args, **kwargs)
        if self.request:
            self.session = self.request.session
        else:
            self.session = {}

    def get_setting(self, name):
        return getattr(settings, name)

    def request_data(self, merge=True):
        if not self.request:
            return {}
        if merge:
            data = self.request.REQUEST
        elif self.request.method == 'POST':
            data = self.request.POST
        else:
            data = self.request.GET
        return data

    def request_host(self):
        if self.request:
            return self.request.get_host()

    def redirect(self, url):
        return HttpResponseRedirect(url)

    def html(self, content):
        return HttpResponse(content, content_type='text/html;charset=UTF-8')

    def render_html(self, tpl=None, html=None, context=None):
        if not tpl and not html:
            raise ValueError('Missing template or html parameters')
        context = context or {}
        try:
            template = loader.get_template(tpl)
        except TemplateDoesNotExist:
            template = loader.get_template_from_string(html)
        return template.render(RequestContext(self.request, context))

    def authenticate(self, *args, **kwargs):
        kwargs['strategy'] = self
        kwargs['storage'] = self.storage
        kwargs['backend'] = self.backend
        return authenticate(*args, **kwargs)

    def session_get(self, name, default=None):
        return self.session.get(name, default)

    def session_set(self, name, value):
        self.session[name] = value
        if hasattr(self.session, 'modified'):
            self.session.modified = True

    def session_pop(self, name):
        self.session.pop(name, None)

    def session_setdefault(self, name, value):
        return self.session.setdefault(name, value)

    def to_session(self, next, backend, *args, **kwargs):
        """Returns dict to store on session for partial pipeline."""
        return {
            'next': next,
            'backend': backend.name,
            'args': tuple(map(self._ctype, args)),
            'kwargs': dict((key, self._ctype(val))
                                for key, val in kwargs.items())
        }

    def from_session(self, session):
        """Takes session saved data to continue pipeline and merges with any
        new extra argument needed. Returns tuple with next pipeline index
        entry, arguments and keyword arguments to continue the process."""
        next, backend, args, kwargs = super(DjangoStrategy, self).\
                                            from_session(session)
        return next, backend, \
               list(map(self._model, args)), \
               dict((key, self._model(val)) for key, val in kwargs.items())

    def build_absolute_uri(self, path=None):
        if self.request:
            return self.request.build_absolute_uri(path)
        else:
            return path

    def random_string(self, length=12, chars=BaseStrategy.ALLOWED_CHARS):
        try:
            from django.utils.crypto import get_random_string
        except ImportError:  # django < 1.4
            return super(DjangoStrategy, self).random_string(length, chars)
        else:
            return get_random_string(length, chars)

    def _ctype(self, val):
        """Converts values that are instance of Model to a dictionary
        with enough information to retrieve the instance back later."""
        if isinstance(val, Model):
            val = {
                'pk': val.pk,
                'ctype': ContentType.objects.get_for_model(val).pk
            }
        return val

    def _model(self, val):
        """Converts back the instance saved by self._ctype function."""
        if isinstance(val, dict) and 'pk' in val and 'ctype' in val:
            ctype = ContentType.objects.get_for_id(val['ctype'])
            ModelClass = ctype.model_class()
            val = ModelClass.objects.get(pk=val['pk'])
        return val

    def is_response(self, value):
        return isinstance(value, HttpResponse)
