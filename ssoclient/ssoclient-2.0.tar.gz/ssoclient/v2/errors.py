# Copyright 2013 Canonical Ltd. This software is licensed under
# the GNU Affero General Public License version 3 (see the file
# LICENSE).
class UnexpectedApiError(Exception):
    pass


class ServerError(UnexpectedApiError):
    """An unexpected 5xx response"""
    def __init__(self, response, msg="", json=None):
        self.response = response
        self.json_body = json
        super(ServerError, self).__init__(
            "%s : %s - %s" % (response.status_code, response.text, msg)
        )


class ClientError(UnexpectedApiError):
    """An unexpected 4xx response"""
    def __init__(self, response, msg="", json=None):
        self.response = response
        self.json_body = json
        super(ClientError, self).__init__(
            "%s : %s - %s" % (response.status_code, response.text, msg)
        )


class ApiException(Exception):
    """An expected/understood 4xx or 5xx response.

    Parses the standard api error reponse format.
    """
    def __init__(self, response, body=None, msg=None):
        body = body or {}
        self.response = response
        self.body = body
        self.error_message = body.get('message')
        self.extra = body.get('extra', {})
        if msg is None:
            # code *should* be the same as the error_code attribute
            # but won't be for raising an ApiException directly instead
            # of a subclass - so still fetch it from the payload body
            code = body.get('code')
            msg = "%s: %s" % (response.status_code, code)
            extra = ', '.join('%s: %r' % i for i in self.extra.iteritems())
            if extra:
                msg += ' (%s)' % extra
        super(ApiException, self).__init__(msg)


class InvalidData(ApiException):
    error_code = "INVALID_DATA"
    status_code = 400


class CaptchaRequired(ApiException):
    error_code = "CAPTCHA_REQUIRED"
    status_code = 401


class InvalidCredentials(ApiException):
    error_code = "INVALID_CREDENTIALS"
    status_code = 401


class TwoFactorRequired(ApiException):
    error_code = "TWOFACTOR_REQUIRED"
    status_code = 401


class AccountSuspended(ApiException):
    error_code = "ACCOUNT_SUSPENDED"
    status_code = 403


class AccountDeactivated(ApiException):
    error_code = "ACCOUNT_DEACTIVATED"
    status_code = 403


class AccountLocked(ApiException):
    error_code = "ACCOUNT_LOCKED"
    status_code = 403


class EmailInvalidated(ApiException):
    error_code = "EMAIL_INVALIDATED"
    status_code = 403


class CanNotResetPassword(ApiException):
    error_code = "CAN_NOT_RESET_PASSWORD"
    status_code = 403


class CaptchaFailure(ApiException):
    error_code = "CAPTCHA_FAILURE"
    status_code = 403


class TooManyTokens(ApiException):
    error_code = "TOO_MANY_TOKENS"
    status_code = 403


class TwoFactorFailure(ApiException):
    error_code = "TWOFACTOR_FAILURE"
    status_code = 403


class PasswordPolicyError(ApiException):
    error_code = "PASSWORD_POLICY_ERROR"
    status_code = 403


class ResourceNotFound(ApiException):
    error_code = "RESOURCE_NOT_FOUND"
    status_code = 404


class AlreadyRegistered(ApiException):
    error_code = "ALREADY_REGISTERED"
    status_code = 409


class TooManyRequests(ApiException):
    error_code = "TOO_MANY_REQUESTS"
    status_code = 429


class CaptchaError(ApiException):
    error_code = "CAPTCHA_ERROR"
    status_code = 502
