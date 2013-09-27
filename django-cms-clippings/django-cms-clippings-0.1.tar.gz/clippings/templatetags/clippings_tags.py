# -*- coding: utf-8 -*-
import re

from classytags.arguments import Argument
from classytags.core import Options
from classytags.helpers import InclusionTag

from cms.models import Placeholder as PlaceholderModel
from cms.plugin_rendering import render_placeholder
from cms.utils import get_language_from_request, get_cms_setting

from django import template
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.mail import mail_managers
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from clippings.models import Clipping


register = template.Library()


def get_site_id(site):
    if site:
        if isinstance(site, Site):
            site_id = site.id
        elif isinstance(site, int) or \
                (isinstance(site, basestring) and site.isdigit()):
            site_id = int(site)
        else:
            site_id = settings.SITE_ID
    else:
        site_id = settings.SITE_ID
    return site_id


CLEAN_KEY_PATTERN = re.compile(r'[^a-zA-Z0-9_-]')


def _report_clipping_error(exception, subject, body):
    if settings.DEBUG:
        raise exception(body)
    else:
        if settings.SEND_BROKEN_LINK_EMAILS:
            mail_managers(subject, body, fail_silently=True)


def _report_missing_clipping(lookup, request):
    site = Site.objects.get_current()
    subject = _('Clipping not found on %s') % site.domain
    body = _("The show_clipping template tag couldn't find the clipping with"
             " lookup arguments `%(lookup)s\n`. The URL of the request was:"
             " http://%(site)s%(path)s") % {'lookup': lookup,
                                            'site': site.domain,
                                            'path': request.path}
    _report_clipping_error(Clipping.DoesNotExist, subject, body)


def _clean_key(key):
    return CLEAN_KEY_PATTERN.sub('-', key)


def _get_cache_key(name, clipping_lookup, lang, site_id):
    if isinstance(clipping_lookup, Clipping):
        clipping_key = str(clipping_lookup.pk)
    else:
        clipping_key = str(clipping_lookup)
    clipping_key = _clean_key(clipping_key)
    return name + '__clipping_lookup:' + clipping_key + '_site:'\
        + str(site_id) + '_lang:' + str(lang)


def _get_clipping(clipping_lookup, request, site_id):
    if clipping_lookup is None:
        return request.current_page

    if isinstance(clipping_lookup, basestring):
        clipping_lookup = {'identifier': clipping_lookup}
    else:
        raise TypeError('The clipping_lookup argument must be a String.')

    clipping_lookup.update({'site': site_id})

    try:
        return Clipping.objects.get(**clipping_lookup)
    except Clipping.DoesNotExist:
        if getattr(settings, "REPORT_MISSING_CLIPPING", False):
            _report_missing_clipping(clipping_lookup, request)
        return None


def _show_clipping_contents(context, clipping_lookup, lang=None, site=None,
                            cache_result=True):
    request = context.get('request', False)
    site_id = get_site_id(site)
    cache_key = None

    if not request:
        return {'content': ''}
    if lang is None:
        lang = get_language_from_request(request)

    if cache_result:
        base_key = _get_cache_key('_show_placeholder_for_clipping',
                                  clipping_lookup, lang, site_id)
        cache_key = _clean_key('%s_placeholder:content' % base_key)
        cached_value = cache.get(cache_key)
        if isinstance(cached_value, basestring):
            return {'content': mark_safe(cached_value)}

    clipping = _get_clipping(clipping_lookup, request, site_id)

    if not clipping:
        return {'content': ''}

    try:
        placeholder = clipping.content
    except PlaceholderModel.DoesNotExist:
        return {'content': ''}
    content = render_placeholder(placeholder, context, "content")
    if cache_result:
        cache.set(cache_key, content,
                  get_cms_setting('CACHE_DURATIONS')['content'])

    if content:
        return {'content': mark_safe(content)}
    return {'content': ''}


class ShowClipping(InclusionTag):
    template = 'clippings/content.html'
    name = 'show_clipping'

    options = Options(
        Argument('identifier'),
        Argument('lang', required=False, default=None),
        Argument('site', required=False, default=None),
        Argument('cache', required=False, default=False),
    )

    def get_context(self, *args, **kwargs):
        return _show_clipping_contents(**self.get_kwargs(*args, **kwargs))

    def get_kwargs(self, context, identifier, lang, site, cache):
        return {
            'context': context,
            'clipping_lookup': identifier,
            'lang': lang,
            'site': site,
            'cache_result': bool(cache),
        }


register.tag(ShowClipping)
register.tag('show_clipping', ShowClipping)
