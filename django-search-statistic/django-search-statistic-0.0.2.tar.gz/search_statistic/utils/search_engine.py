# coding: utf-8
from django.utils.translation import ugettext_lazy as _
from urlparse import urlparse, parse_qs

import re


class SearchEngine(object):

    abstract = True
    verbose_name = None
    key = None

    # host_pattern = re.compile('.*')
    # query_parameter = 'query'

    @classmethod
    def get_key(cls):
        return vars(cls).get('key', cls.__name__.lower()[0:15])

    @classmethod
    def get_verbose_name(cls):
        return vars(cls).get('verbose_name', cls.__name__)

    @classmethod
    def extract_query(cls, request):
        referer = request.META.get("HTTP_REFERER")
        if not referer:
            return
        url = urlparse(referer)
        if cls.host_pattern.match(url.netloc):
            params = parse_qs(url.query)
            search_query = params.get(cls.query_parameter, [None])[0]
            return search_query and search_query.decode("utf-8").lower()
        return None


class GoogleEngine(SearchEngine):

    verbose_name = _('google')
    key = 'google'
    host_pattern = re.compile('.*google\..*')
    query_parameter = 'q'


class YandexEngine(SearchEngine):

    verbose_name = _('yandex')
    key = 'yandex'
    host_pattern = re.compile('.*(ya)|(yandex)\..*')
    query_parameter = 'text'


class RamblerEngine(SearchEngine):

    verbose_name = _('rambler')
    key = 'rambler'
    host_pattern = re.compile('.*rambler\..*')
    query_parameter = 'query'


class GoMailEngine(SearchEngine):

    verbose_name = _('go.mail')
    key = 'go.mail'
    host_pattern = re.compile('.*go\.mail\..*')
    query_parameter = 'q'


class BingEngine(SearchEngine):

    verbose_name = _('bing')
    key = 'bing'
    host_pattern = re.compile('.*bing\..*')
    query_parameter = 'q'


class SearchYahooEngine(SearchEngine):

    verbose_name = _('yahoo search')
    key = 'yahoo'
    host_pattern = re.compile('.*search\.yahoo\..*')
    query_parameter = 'p'


class AskEngine(SearchEngine):

    verbose_name = _('ask')
    key = 'ask'
    host_pattern = re.compile('.*ask\..*')
    query_parameter = 'q'


class SearchQipEngine(SearchEngine):

    verbose_name = _('QIP search')
    key = 'qip'
    host_pattern = re.compile('.*search\.qip\..*')
    query_parameter = 'query'


def all_engines(cls=SearchEngine):
    return cls.__subclasses__() + [
        g for s in cls.__subclasses__()
        for g in all_engines(s)
        if vars(g).get('abstract', False)
    ]


def search_engine_choices():
    choices = [(
        engine.get_key(),
        engine.get_verbose_name().title()
    ) for engine in all_engines()]
    choices.sort(key=lambda ob: ob[0])
    return choices
