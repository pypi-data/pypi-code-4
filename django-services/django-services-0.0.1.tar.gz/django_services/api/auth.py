# encoding: utf-8
import re
import logging
from rest_framework import authentication
from rest_framework import exceptions
from plugins.keystone.service import KeystoneService

LOG = logging.getLogger(__name__)
AWS_AUTHORIZATION_HEADER_FORMAT = re.compile(r'\AAWS ([^:]+):(.*)\Z')


class KeystoneAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        match = AWS_AUTHORIZATION_HEADER_FORMAT.match(request.META.get('HTTP_AUTHORIZATION', ''))
        if match:
            # validate required headers
            for header in ['HTTP_DATE', 'CONTENT_TYPE']:
                if header not in request.META:
                    LOG.info(u'invalid aws authentication. No header %s' % header)
                    raise exceptions.AuthenticationFailed('No Header %s' % header)

            access_key = match.group(1)
            signature = match.group(2)
            verb = request.method
            path = request.get_full_path()
            content = request.body

            content_type = request.META['CONTENT_TYPE']
            date = request.META['HTTP_DATE']
            user, tenant = self.validate_rest_request(access_key,
                                                      signature,
                                                      verb,
                                                      path,
                                                      date,
                                                      content,
                                                      content_type)
            if not user or not tenant:
                LOG.info(u'Invalid credentiais')
                raise exceptions.AuthenticationFailed('No AWS credentiais')

            # put user in request
            # Do not use django.contrib.auth.login method, because I don't want a new session on every api call
            request._request.user = user
            return user, None

        # This request probably will be authenticated by another provider (or is unauthenticated)
        LOG.debug(u'No header http authentication or not in format "AWS xxx:xxx"')
        return None

    def keystone(self):
        return KeystoneService()

    def validate_rest_request(self, access_key, signature, verb, path, date, content, content_type):
        user, tenant = self.keystone().validate_rest_request(access_key,
                                                             signature,
                                                             verb,
                                                             path,
                                                             date,
                                                             content,
                                                             content_type)
        return user, tenant
