import werkzeug.exceptions as ex
from db2rest.helpers import is_json_request
from simplejson import JSONEncoder as encoder


class HTTPExceptionMixin(ex.HTTPException):
    """In order to be rest complaint redefine some
       method of werkzeug HTTPException.
    """
    def get_response(self, environ):
        """Return a json response for a json request
           otherwise an html response
        """
        resp = super(HTTPExceptionMixin, self).get_response(environ)
        if is_json_request(environ.get('HTTP_ACCEPT')):
            resp.mimetype = environ['HTTP_ACCEPT']
        return resp

    def get_body(self, environ=None):
        """Return the body with the right message in case of
            json request.
        """
        body = super(HTTPExceptionMixin, self).get_body(environ)
        if is_json_request(environ.get('HTTP_ACCEPT')):
            body = dict(detail=self.body_message)
            body = encoder().encode(body)
        return body

    @property
    def body_message(self):
        """The subclass is repsonsible to impleement this
           method.
        """
        raise NotImplemented("""The subclass is repsonsibile
                                to implemet this method""")


class MethodNotAllowed(ex.MethodNotAllowed,  HTTPExceptionMixin):
    """Return a proper messagge error for not allowed operation."""
    def __init__(self, description, valid_methods, method):
        super(MethodNotAllowed, self).__init__(description=description,
                                               valid_methods=valid_methods)
        self.method = method

    @property
    def body_message(self):
        return "The method %s is not allowed" % self.method.upper()


class NotFound(ex.NotFound, HTTPExceptionMixin):
    """Return a praper body message for not found resource"""
    @property
    def body_message(self):
        return "Resource Not Found"


class Unauthorized(ex.Unauthorized, HTTPExceptionMixin):
    """Return a praper body message and headers for unauthorized requests."""
    @property
    def body_message(self):
        return "Login Required"

    def get_headers(self, enviro):
        super(HTTPExceptionMixin, self).get_headers(enviro)
        return {'WWW-Authenticate': 'Basic realm="/"'}
