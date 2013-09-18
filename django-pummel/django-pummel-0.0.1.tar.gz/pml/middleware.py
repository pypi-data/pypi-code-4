import random

from django.conf import settings
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.contrib.messages.api import get_messages
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.utils.cache import patch_cache_control
from lxml import etree


class SkipMixin(object):
    def should_skip(self, request):
        path_bypass = [
            reverse('admin:index'),  # Skip for admin
            settings.STATIC_URL,  # Skip for static
            settings.MEDIA_URL,  # Skip for media
        ]

        if hasattr(settings, 'PML_IGNORE_PATH'):
            path_bypass += settings.PML_IGNORE_PATH

        for path in path_bypass:
            if request.path.startswith(path):
                return True
        return False


class FormMiddleware(object):
    def process_request(self, request):
        if request.GET.get('submit'):
            request.method = "POST"
            request.POST = request.POST.copy()
            request.POST.update(request.GET)


class NoCacheMiddleware(SkipMixin, object):
    def process_response(self, request, response):
        if self.should_skip(request):
            return response

        # Set HTTP response cache headers to not cache.
        patch_cache_control(response, no_cache=True, no_store=True, must_revalidate=True)
        return response


class RandomLinkMiddleware(SkipMixin, object):
    def process_response(self, request, response):
        if self.should_skip(request):
            return response

        # Bypass further processing for empty(redirect) response.
        if not response.content:
            return response

        # Add a random get param to all LINK hrefs to further prevent
        # Vodafone gateway from caching.
        try:
            tree = etree.fromstring(response.content)
        except etree.XMLSyntaxError:
            return response
        for link in tree.findall('.//LINK'):
            href = link.get('href')
            if href:
                if '?' in href:
                    href += '&rnd=%s' % random.randint(1000000, 9999999)
                else:
                    href += '?rnd=%s' % random.randint(1000000, 9999999)
                link.set('href', href)
        response.content = etree.tostring(tree)
        return response


class RedirectMiddleware(SkipMixin, object):
    def process_response(self, request, response):
        if self.should_skip(request):
            return response

        if response.__class__ in [HttpResponseRedirect, HttpResponsePermanentRedirect, ]:
            location = response._headers['location'][1]
            if not location.startswith('/admin'):
                url = response._headers['location'][1]
                if '?' in url:
                    url += '&rnd=%s' % str(random.randint(1000000, 9999999))
                else:
                    url += '?rnd=%s' % random.randint(1000000, 9999999)
                return render_to_response('pml/redirect.xml', {'url': url, 'messages': get_messages(request)}, mimetype='text/xml')
        return response


class VLiveRemoteUserMiddleware(RemoteUserMiddleware):
    header = 'HTTP_X_UP_CALLING_LINE_ID'


class XMLResponseMiddleware(SkipMixin, object):
    """
    Sets response mimetype to text/xml.
    """
    def process_response(self, request, response):
        if self.should_skip(request):
            return response

        # When developing on error show trace page
        if settings.DEBUG and response.status_code in [500, ]:
            return response

        # Set xml content type for everything else.
        response['Content-Type'] = 'text/xml'
        return response
