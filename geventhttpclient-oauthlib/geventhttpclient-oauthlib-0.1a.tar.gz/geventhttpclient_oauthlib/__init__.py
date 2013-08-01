# coding=utf-8

from geventhttpclient.client import HTTPClient, URL
from oauthlib.oauth1.rfc5849 import (
    Client, SIGNATURE_HMAC, SIGNATURE_TYPE_AUTH_HEADER)
from oauthlib.common import extract_params

CONTENT_TYPE_FORM = 'application/x-www-form-urlencoded'
CONTENT_TYPE_MULTI = 'multipart/form-data'


class OAUTH1HTTPClient(HTTPClient):
    def __init__(self, *args, **kwargs):
        super(OAUTH1HTTPClient, self).__init__(*args, **kwargs)
        self.client = None

    @classmethod
    def from_url(cls, url, **kw):
        if not isinstance(url, URL):
            url = URL(url)
        enable_ssl = url.scheme == 'https'
        if not enable_ssl:
            kw.pop('ssl_options', None)
        return cls(url.host, port=url.port, ssl=enable_ssl, **kw)

    @classmethod
    def from_oauth_params(
            cls, url, client_key,
            client_secret=None,
            resource_owner_key=None,
            resource_owner_secret=None,
            callback_uri=None,
            signature_method=SIGNATURE_HMAC,
            signature_type=SIGNATURE_TYPE_AUTH_HEADER,
            rsa_key=None, verifier=None, realm=None,
            convert_to_unicode=False, encoding='utf-8',
            **kwargs):
        instance = cls.from_url(url, **kwargs)
        instance.client = Client(
            client_key, client_secret, resource_owner_key,
            resource_owner_secret, callback_uri, signature_method,
            signature_type, rsa_key, verifier)
        return instance

    def _build_request(self, method, request_uri, body=u"", headers={}):
        # oauthlib expects None instead of empty string
        method = unicode(method)
        request_uri = unicode(request_uri)
        extracted_body = extract_params(body)
        if extracted_body:
            # contenttype sometimes is ...form-data; boundary=X
            contenttype = headers.get('Content-Type', '').split(';', 1)[0]
            if contenttype == CONTENT_TYPE_FORM:
                uri, headers, body = self.client.sign(
                    uri=request_uri,
                    http_method=method,
                    body=extracted_body,
                    headers=headers)
            elif contenttype == CONTENT_TYPE_MULTI:
                uri, headers, _discard = self.client.sign(
                    uri=request_uri,
                    http_method=method,
                    body=None,
                    headers=headers)
        else:
            uri, headers, _discard = self.client.sign(
                uri=request_uri,
                http_method=method,
                body=None,
                headers=headers)

        return super(OAUTH1HTTPClient, self)._build_request(
            method, uri, body=body, headers=headers)
