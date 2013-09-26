from mimetypes import guess_type, add_type
add_type('application/json', '.json')

from webob import Response
from webob.dec import wsgify
from webob.exc import HTTPServerError, HTTPBadRequest
from webob.static import FileApp, DirectoryApp

from _term import (
    Hict, parse_json, to_simple, to_json,
    is_file, is_dir, is_generator
)
from _service import consume
from _auth import State

CONTENT_TYPE = 'text/plain'
SERVER = 'FWS/1.0'
CHARSET = 'utf8'

@wsgify
def handler(req):
    _state_ = State(domain = req.host.split(':', 1)[0],
                    ssl = req.scheme == 'https',
                    origin = req.remote_addr,
                    user = None, role = None,
                    sid = None, token = None,
                    data = State())

    req.charset = CHARSET

    argd, params = Hict(), req.params
    for key in params.iterkeys():
        if key.endswith('[]'):
            argd[key[:-2]] = params.getall(key)
        else:
            argd[key] = params[key]

    if req.is_xhr:
        argd.update(parse_json(req.json_body))

    try:
        fun, ext, ret = consume(_state_, req.path, **argd)
    except Exception, e:
        error = to_json(dict(error = to_simple(*e.args)))
        try:
            raise
        except AssertionError:
            return HTTPBadRequest(error)
        except:
            return HTTPServerError()

    if fun.static:
        if is_file(ret):
            res = FileApp(ret)
        elif is_dir(ret):
            res = DirectoryApp(ret)
    elif isinstance(ret, file):
        with ret:
            res = FileApp(ret.name)
    else:
        content_type = guess_type(fun.urlpath+ext)[0] or CONTENT_TYPE
        res = Response(charset = CHARSET, content_type = content_type)

        if isinstance(ret, str):
            res.body = ret
        elif isinstance(ret, unicode):
            res.unicode_body = ret
        elif isinstance(ret, file):
            res.body_file = ret
        elif isinstance(ret, (tuple, list)) or is_generator(ret):
            res.app_iter = ret
        else:
            res.body = repr(ret)

    if not fun.cache:
        res.cache_expires(0)

    res.server = SERVER

    return res
