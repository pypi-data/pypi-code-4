from mimetypes import types_map
from webob import dec, exc, static, Response

from fanery import service, authorize
from fanery.terms import (
    hict, is_file, is_dir, is_string,
    _from_json as parse_json, to_json,
)

SERVER_NAME = 'FWS/1.0'
CONTENT_TYPE = 'text/plain'
JSON_KEY = '_json'

@dec.wsgify
def handler(req):
    # read request params
    try:
        params = req.params
        getall = params.getall
        argd = dict((k, (v[0] if len(v) == 1 else v) or None) for k, v in [
                     (k, [v.strip() for v in getall(k)]) for k in params
                                                  if not k.startswith('_')])
        if JSON_KEY in params:
            argd.update(parse_json(params[JSON_KEY]))
    except Exception, e:
        raise exc.HTTPBadRequest(*e.args)

    # start session state
    service.state.update(ssl = bool(req.scheme == 'https'),
                         domain = req.host.split(':')[0],
                         origin = req.remote_addr)

    # consume remote call
    try:
        call, ext, output, ret = service._consume(req.path, **argd)
        if call.static is True:
            if is_dir(ret):
                return static.DirectoryApp(ret)
            elif is_file(ret):
                if isinstance(ret, file):
                    with ret:
                        ret = ret.name
                if call.force_download is True:
                    return static.FileApp(ret,
                        content_type = "application/force-download",
                        content_disposition = 'attachment; filename="%s"' % ret)
                else:
                    return static.FileApp(ret)
            else:
                raise service.NotFound(ret)
        else:
            res = Response(content_type = types_map.get(ext, CONTENT_TYPE))
            res.body_file.write(ret if is_string(ret) else to_json(ret))
            res.cache_expires(call.cache)
            res.server = SERVER_NAME
            res.md5_etag()
            return res
    except service.NotFound, e:
        raise exc.HTTPNotFound()
    except (NotImplementedError, service.UnknownFormatter), e:
        raise exc.HTTPNotImplemented(*e.args)
    except AssertionError, e:
        res = Response(content_type = CONTENT_TYPE)
        res.status_code = 400 # bad request
        error = dict(type = e.__class__.__name__, reason = e.args)
        res.body_file.write(to_json(error))
        return res
    except Exception, e:
        raise exc.HTTPInternalServerError(*e.args)

'''
try:
    from gevent import ...
except ImportError:
    try:
        from cherrypy.wsgiserver import CherryPyWSGIServer
    except ImportError:
        from wsgiref import ....
'''
