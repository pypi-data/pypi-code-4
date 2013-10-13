from __future__ import absolute_import

import json

from bottle import request, response

from .collections import merge
from .json import escape


class JsonBottle(object):

  def __init__(self, app):
    self.app = app

  def __getattr__(self, key):
    return getattr(self.app, key)

  def cors(self, decorated):
    """Attach CORS (Cross Origin Resource Headers) headers to enable cross-site AJAX

    >>> app = SuperBottle(bottle.Bottle())
    >>> @app.cors
    ... @app.route("/hello", method=["OPTIONS", "GET"])   # OPTIONS is necessary here!
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
      kwargs.update(json_args(request))
      return decorated(*args, **kwargs)
    return decorator

  def json_output(self, decorated):
    """Function outputs JSON"""
    def decorator(*args, **kwargs):
      # escape output of function
      output = escape(decorated(*args, **kwargs))

      # return it as a string
      response.content_type = "application/json"
      response.body = json.dumps(output)

      return response

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
      # need at least these method types. Add to list of already passed
      method = ['GET', 'POST', 'OPTIONS'] + kwargs.get("method", [])
      kwargs['method'] = list(set(method))

      f = self.json_output(f)
      f = self.json_input(f)
      f = self.cors(f)
      f = self.route(*args, **kwargs)(f)
      return f
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
  # from POSTed content
  if r.json is not None:
    return r.json
  else:
    # from body
    try:
      r.body.seek(0)
      return json.loads(r.body.read())
    except ValueError:
      # from params dict
      return dict(r.params)


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
