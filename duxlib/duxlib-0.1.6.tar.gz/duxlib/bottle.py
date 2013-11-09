from __future__ import absolute_import

from StringIO import StringIO
import gzip
import json

import bottle
from bottle import request, response

from .collections import merge
from .json import escape
from .gzip import encode as gzip_encode


class JsonBottle(object):

  def __init__(self, app):
    self.app = app

  def __getattr__(self, key):
    return getattr(self.app, key)

  def gzip(self, decorated):
    """Enable gzip compression on requests

    >>> app = SuperBottle(bottle.Bottle())
    >>> @app.get("/hello")
    ... @app.gzip
    ... def method(name):
    ...   response = bottle.response
    ...   response.body = "Hello, {}".format(name)
    ...   return response   # must return response object!
    """

    def decorator(*args, **kwargs):
      # assumes that decorated function returns bottle.response or a string
      response = decorated(*args, **kwargs)
      if not isinstance(response, bottle.Response):
        if isinstance(response, basestring):
          bottle.response.body = response
          response = bottle.response
        else:
          raise bottle.BottleException(
              "SuperBottle.gzip expects decorated"
              "function to return a bottle.Response object of a string"
          )

      if 'Accept-Encoding' in request.headers:
        encodings = [s.strip().lower() for s in request.headers['Accept-Encoding'].split(",")]
        if 'gzip' in encodings:
          response.body = gzip_encode(response.body)
          response.headers['Content-Encoding'] = 'gzip'

      return response
    return decorator

  def cors(self, decorated):
    """Attach CORS (Cross Origin Resource Headers) headers to enable cross-site AJAX

    >>> app = SuperBottle(bottle.Bottle())
    >>> @app.route("/hello", method=["OPTIONS", "GET"])   # OPTIONS is necessary here!
    ... @app.cors
    ... def method(name):
    ...   return "Hello, {}".format(name)
    """
    def decorator(*args, **kwargs):
      # update headers with CORS junk
      response.headers.update(cors_headers(request))

      if request.method.upper() == 'OPTIONS':
        # an OPTIONS request is a "preflight" request sent before a cross-site
        # AJAX request is made. It's done by most modern browsers to make sure
        # that the next GET/POST/whatever request is allowed by the server.
        return None
      else:
        return decorated(*args, **kwargs)

    return decorator
  def json_input(self, decorated):
    """Function parses input from JSON body or GET parameters"""
    def decorator(*args, **kwargs):
      # get args determined by JSON input
      try:
        kwargs.update(json_args(request))
      except Exception as e:
        request.body.seek(0)
        raise JsonInputException("Unable to parse JSON arguments: {}".format(request.body.read()))
      return decorated(*args, **kwargs)
    return decorator

  def json_output(self, decorated):
    """Function outputs JSON"""
    def decorator(*args, **kwargs):
      # escape output of function
      output = escape(decorated(*args, **kwargs))

      # return it as a string
      response.content_type = "application/json"
      try:
        response.body = json.dumps(output)
        return response
      except (ValueError, TypeError) as e:
        raise JsonOutputException("Unable to encode output as JSON: {}".format(output))

    return decorator

  def json_route(self, *args, **kwargs):
    """Treat this function as JSON endpoint

    >>> @app.json_route("/hello")
    ... def hello(name):
    ...   return {"status": "success", "response": "Hello, " + name}

    ```bash
    $ http post http://localhost:8000/hello <<< '{"name": "duxlib"}'
    ```

    Parameters
    ----------
    Same as Bottle.route
    """

    def decorator_(f):
      # HTTP methods by which this route can be accessed. CORS requires
      # 'OPTIONS'; otherwise, assume it's a GET/POST request.
      if 'method' in kwargs:
        method = list(set(kwargs['method'] + ['OPTIONS']))
      else:
        method = ['GET', 'POST', 'OPTIONS']
      kwargs['method'] = method

      f = self.json_output(f)
      f = self.gzip(f)
      f = self.json_input(f)
      f = self.cors(f)
      f = self.on_exception(Exception)(f)
      f = self.route(*args, **kwargs)(f)
      return f
    return decorator_

  def on_exception(self, exceptions=Exception, callback=None):
    """Catch exceptions thrown by decorated function and respond with a callback

    Parameters
    ----------
    exceptions : tuple or Exception
        exceptions to catch
    callback : None or function
        Callback applied when an exception is thrown. If callback is None, a
        dict with the exception's details is returned; otherwise, the
        callback's output is returned.
    """

    def decorator_(f):
      def decorator(*args_, **kwargs_):
        try:
          return f(*args_, **kwargs_)
        except exceptions as e:
          if callback is None:
            return {
                "status"    : "exception",
                "exception" : e.__class__.__name__ + ": " + str(e)
              }
          else:
            return callback(e)
      return decorator
    return decorator_


def json_args(r):
  """Get JSON arguments to this request

  There are 3 ways to pass arguments to a function via a bottle request

  1. `bottle.request.json`
  2. as a JSON object in `bottle.request.body`
  3. as an HTTP GET parameters dict

  These options are taken in this order. Thus, if `bottle.request.json` is
  non-empty, then options 2. and 3. will be ignored.

  Parameters
  ----------
  r : bottle.request

  Returns
  -------
  kwargs : dict
      collected keyword arguments from request
  """
  r.body.seek(0)
  content = r.body.read()
  if content:
    # body is assumed to be JSON-encoded content
    return json.loads(content)
  elif r.method.upper() == "GET":
    # GET parameters might be specified
    return dict(r.params)
  else:
    # no parameters here
    return {}


def cors_headers(r):
  """Construct headers to attach to enable cross-domain AJAX requests

  Parameters
  ----------
  r : bottle.request

  Returns
  -------
  headers : dict
      `dict` with CORS headers. Update `bottle.request.headers` with these to
      enable cross site AJAX requests.
  """
  # make sure cross site scripting AJAX requests headers are set
  headers = {}
  headers['Access-Control-Allow-Origin']  = r.headers.get(
      "Origin",
      "*"
  )
  headers['Access-Control-Allow-Methods'] = r.headers.get(
      "Access-Control-Request-Method",
      'GET, POST, OPTIONS'
  )
  headers['Access-Control-Allow-Headers'] = r.headers.get(
      "Access-Control-Request-Headers",
      'Origin, Accept, Content-Type, X-Requested-With'
  )
  return headers


class JsonInputException(bottle.BottleException):
  pass


class JsonOutputException(bottle.BottleException):
  pass
