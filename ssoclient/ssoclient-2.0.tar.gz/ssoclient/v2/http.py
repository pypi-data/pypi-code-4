# Copyright 2013 Canonical Ltd. This software is licensed under
# the GNU Affero General Public License version 3 (see the file
# LICENSE).
import functools
import json

import requests

from ssoclient.v2 import errors

JSON_MIME_TYPE = 'application/json'
ERRORS = {
    e.error_code: e for e in [
        errors.AccountDeactivated,
        errors.AccountLocked,
        errors.AlreadyRegistered,
        errors.AccountSuspended,
        errors.CanNotResetPassword,
        errors.CaptchaError,
        errors.CaptchaFailure,
        errors.CaptchaRequired,
        errors.EmailInvalidated,
        errors.InvalidCredentials,
        errors.InvalidData,
        errors.PasswordPolicyError,
        errors.ResourceNotFound,
        errors.TooManyRequests,
        errors.TooManyTokens,
        errors.TwoFactorFailure,
        errors.TwoFactorRequired,
    ]
}


class V2ApiClientResponse(object):
    """A successful response from an API call to the v2 SSO API."""

    def __init__(self, status_code, content):
        super(V2ApiClientResponse, self).__init__()
        self.status_code = status_code
        self.content = content
        self.ok = True  # backwards compat with requests' Response

    def json(self):
        """Return this instance's content, available for backwards compat."""
        return self.content


def process_response(func):
    """Decorator to parse 'func' responses and manage errors."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Wrapper for func."""

        response = func(*args, **kwargs)
        try:
            json_body = response.json()
        except (ValueError, TypeError):
            # simplejson raises JSONDecodeError for invalid json
            # json raises ValueError. JSONDecodeError is a subclass
            # of ValueError - so this catches either.
            json_body = {}

        if response.ok:
            # return the json-decoded value and the status code
            return V2ApiClientResponse(
                status_code=response.status_code, content=json_body)

        # from now on, just error management
        code = json_body.get('code')
        exc = ERRORS.get(code)
        if exc is not None:
            # raise a specific exception
            raise exc(response, json_body)

        if code:
            msg = "Unknown error code '%s' in response" % code
        else:
            msg = "No error code in response"

        if response.status_code < 500:
            exc = errors.ClientError
        else:
            exc = errors.ServerError
        raise exc(response, msg, json_body)

    return wrapper


class ApiSession(requests.Session):
    """An SSO api specfic Session

    Adds support for a url endpoint, 500 exceptions, and JSON request body
    handling.
    """

    def __init__(self, endpoint):
        super(ApiSession, self).__init__()
        self.endpoint = endpoint.rstrip('/') + '/'
        # sent with every request
        self.headers['Accept'] = JSON_MIME_TYPE

    @process_response
    def request(self, method, url, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data'])
            kwargs['headers']['Content-Type'] = JSON_MIME_TYPE
        url = self.endpoint + url.lstrip('/')
        response = super(ApiSession, self).request(method, url, **kwargs)
        return response
