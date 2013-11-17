#coding: utf-8
import os, sys, traceback, json, imp, types, mimetypes, logging, glob
import datetime
from StringIO import StringIO
import Cheetah.Template
from app import BaseApp
import connect
from session import RedisSession
from httprequest import HttpRequest
from httpresponse import HttpResponse
from utils import U
from utils import JsonEncoder


def logging_exc(env, message=""):
    """记录异常日志"""
    msg = "\n".join(traceback.format_exception(*sys.exc_info()))
    logging.error("PATH_INFO: %s\n" % env.get("PATH_INFO",""))
    logging.error("QUERY_STRING: %s\n" % env.get("QUERY_STRING",""))
    if message!="":
        logging.error("MESSAGE: %s\n" % message)
    logging.error(msg)


class NullMiddleware(object):
    def __call__(self, environ, start_response):
        start_response("301 ", [("content-type", "text/html")])
        return ["<h1>No entry to handle your request</h1>"]


class BaseMiddleware(object):
    DEFAULT_HEADERS = {
            "content-type": "text/html;charset=utf-8",
    }
    SESSION_COOKIE_NAME = ""

    def __init__(self, application):
        assert callable(application)
        self.application = application


    def get_session(self, req, domain=""):
        """取得session对象"""
        if self.SESSION_COOKIE_NAME=="":
            return None

        sessid = req.get(self.SESSION_COOKIE_NAME, "").strip()
        if sessid == "": 
            ck = req.cookies.get(self.SESSION_COOKIE_NAME)
            if ck!=None:
                sessid = ck.value
            else:
                sessid = None
        
        rdb = connect.connect_redis()
        sess = RedisSession(rdb, sessid=sessid, domain=domain)
        return sess


    def get_request(self, env):
        """取得HttpRequest对象"""
        if 'wae.request' in env:
            return env['wae.request']
        else:
            req = HttpRequest(env, env['wsgi.input'])
            env['wae.request'] = req
            return req

    def get_response(self, env):
        """取得HttpResponse对象"""
        if 'wae.response' in env:
            res = env['wae.response']
        else:
            res = HttpResponse()
            env['wae.response'] = res

        for k, v in self.DEFAULT_HEADERS.items():
            if k.lower() not in res.headers:
                res.set_header(k, v)
        return res


class UserMiddleware(BaseMiddleware):
    "识别用户Middlware"

    def do_check_user(self, req, sess):
        "检测用户"
        return None

    def pre_processor(self, pathinfo, request, response, session):
        """前期处理. 如果返回不为None,表示后续处理中止"""
        pass

    def user_identified(self, env, start_response):
        """用户已识别"""
        return self.application(env, start_response)

    def user_not_identified(self, env, start_response):
        "用户不能识别"
        return [json.dumps({"status":-1, "message":"not signed-in yet"})]


    def __call__(self, env, start_response):
        assert self.SESSION_COOKIE_NAME != ""

        req = self.get_request(env)
        res = self.get_response(env)

        # session
        session = self.get_session(req)
        env['wae.session'] = session

        pi = env['PATH_INFO']
        if pi.startswith("/"): pi=pi[1:]

        # pre-processor
        ret = self.pre_processor(pi, req, res, session)
        if ret!=None:
            if type(ret)==types.StringType:
                out = [ret]
            elif type(ret)==types.UnicodeType:
                out = [ret.encode("utf-8")]
            elif hasattr(ret, "read"):
                # file-like object
                ret.seek(0)
                if 'wsgi.file_wrapper' in env:
                    out = env['wsgi.file_wrapper'](ret, BLOCK_SIZE)
                else:
                    out = FileWrapper(ret)
            else:
                try:
                    data = json.dumps(U(ret), cls=JsonEncoder)
                except:
                    logging_exc(env)
                    res.set_status(500)
                    out = ["<h1>数据不能转换为JSON</h1>"]
                    data = None

                if data!=None:
                    callback = req.get("callback", "")
                    if callback!="":
                        out = ["%s(%s);" % (callback, data)]
                    else:
                        out = [data]
            
            start_response('%d ' % res.status, res.headers.items())
            return out

        if self.do_check_user(req, session) in (None, False):
            start_response('401 ', res.headers.items())
            return self.user_not_identified(env, start_response)
        else:
            return self.user_identified(env, start_response) 


class RouterMiddleware(BaseMiddleware):
    """路由中间件"""
    def __init__(self, application, pkg):
        super(RouterMiddleware, self).__init__(application)
        assert pkg[-1] not in (".", "/"), pkg
        assert pkg[0] not in (".", "/"), pkg

        self._pkg = pkg
        self._path = None
        self._router_map = {}
        self._cls2path_map = {}
        self.load_map()


    def _collect_app_from_module(self, module, modstack, path):
        """收集module中的应用App对象"""
        assert len(modstack)>0
        mn = ".".join(modstack)

        for name, o in vars(module).items():
            if type(o) is not types.TypeType:
                continue
                    
            if not issubclass(o, BaseApp) or o==BaseApp:
                continue

            if o.__module__ != mn:
                continue

            # class template path
            lst = [x for x in path]
            if name!="main": lst.append(name)
            if len(lst)>0:
                self._cls2path_map[o] = "%s/%s" % (self._path, "/".join(lst))
            else:
                self._cls2path_map[o] = self._path

            for c in reversed(type.mro(o)):
                for pname in dir(c):
                    prop = getattr(c, pname, None)
                    if type(prop) is not types.MethodType:
                        continue
                            
                    if not hasattr(prop, "exposed"):
                        continue

                    v = {
                        "class":o, 
                        "method":prop, 
                        "exposed":getattr(prop, "exposed"),
                    }

                    lst = [x for x in path]
                    if name!="main": lst.append(name)

                    if pname=="index":
                        k = "/".join(lst)
                        self._router_map[k] = v 
                        logging.info("    %s => %s.%s" % (k, name, pname))

                    lst.append(pname)
                    k = "/".join(lst)
                    self._router_map[k] = v
                    logging.info("    %s => %s.%s" % (k, name, pname))


    def _do_load_map(self, modstack, path):
        if path==None:
            try:
                m = __import__(".".join(modstack), fromlist=[''])
                self._path = os.path.dirname(m.__file__)
                path = []
                self._collect_app_from_module(m, modstack, [])

            except ImportError, e:
                logging.warn("cannot import '%s'" % ".".join(modstack))
                return
        
        for f in glob.glob("%s/*" % "/".join([self._path]+path)):
            bn = os.path.basename(f)

            if os.path.isdir(f):
                if not os.path.exists("%s/__init__.py" % f):
                    continue
            else:
                if bn in (".", "..", "__init__.py") or not bn.endswith(".py"):
                    continue
                bn = bn[:-3]

            a = modstack+[bn]
            mname = ".".join(a)
            msg = "check %s" % mname
            try:
                m = __import__(mname, fromlist=[''])
            except ImportError, e:
                msg += " ... fail"
                continue
            finally:
                logging.info(msg)

            if os.path.isdir(f):
                self._collect_app_from_module(m, a, path+[bn])    # check app_class in __init__.py
                self._do_load_map(modstack+[bn], path+[bn])       # recursive load
            else:
                self._collect_app_from_module(m, a, path)

    def load_map(self):
        """加载路由地图"""
        self._router_map = {}
        self._cls2path_map = {}
        self._do_load_map([self._pkg], None)


    def _find_entry(self, pathinfo, reqmet):
        """路径匹配应用入库"""
        assert not pathinfo.startswith("/"), pathinfo 
        assert not pathinfo.endswith("/"), pathinfo

        def _esc(v):
            return v.replace("#", "").replace("-", "_").replace(".", "_")

        token = [x.strip() for x in pathinfo.split("/") if x.strip()!=""]
        n = len(token)

        args = []
        while len(token)>0:
            k = "/".join(_esc(x) for x in token)
            if k in self._router_map:
                e = self._router_map[k]
                if reqmet in e['exposed']:
                    return e['class'], e['method'], args
            args.insert(0, token[-1])
            token = token[:-1]

        return (None, None, None)


    def _run(self, env, start_response, appcls, func, args):
        "执行App"
        assert issubclass(appcls, BaseApp)
        assert type(func) is types.MethodType

        req = self.get_request(env)
        res = self.get_response(env)
        sess = self.get_session(req)

        try:
            ainst = appcls(env, req, res, sess)
            ainst.initialize()
            ret = func(ainst, *args)

        except AssertionError, e:
            ainst.abort()
            logging_exc(env)
            start_response('500 ', res.headers.items())
            return [json.dumps({"status":-1, "message":e.message}, ensure_ascii=False, cls=JsonEncoder)]

        except:
            ainst.abort()
            logging_exc(env)
            start_response('500 ', res.headers.items())
            return [json.dumps({"status":-1, "message":ainst.errmsg}, ensure_ascii=False, cls=JsonEncoder)]

        # 返回结果
        if len(res.cookies)>0 and hasattr(start_response, 'set_cookie'):
            # for FAPWS return cookie
            for k, v in res.cookies.items():
                start_response.set_cookie(k, v)
       
        if ret==None or isinstance(ret, Cheetah.Template.Template):
            if ret==None:
                ret = ainst.render_template(func.__name__, dirmap=self._cls2path_map)

            try:
                out = [str(ret)]
            except:
                logging_exc(env)
                res.set_status(300)
                out = [json.dumps({"status":-1, "message":"cannot convert return data to json"}, ensure_ascii=False)]

        else:
            if type(ret)==types.StringType:
                out = [ret]
            elif type(ret)==types.UnicodeType:
                out = [ret.encode("utf-8")]
            elif hasattr(ret, "read"):
                # file-like object
                ret.seek(0)
                if 'wsgi.file_wrapper' in env:
                    out = env['wsgi.file_wrapper'](ret, BLOCK_SIZE)
                else:
                    out = FileWrapper(ret)
            else:
                try:
                    data = json.dumps(U(ret), cls=JsonEncoder)
                except:
                    logging_exc(env)
                    res.set_status(500)
                    out = ["<h1>数据不能转换为JSON</h1>"]
                    data = None

                if data!=None:
                    callback = req.get("callback", "")
                    if callback!="":
                        out = ["%s(%s);" % (callback, data)]
                    else:
                        out = [data]

        ainst.finalize()
        start_response("%d " % res.status, res.headers.items())
        return out


    def _check_buildin_cmd(self, pathinfo, env):
        """检测内部命令"""
        pi = pathinfo.lower()
        if pi=="@router/list":
            return self._router_map.keys()


    def __call__(self, environ, start_response):
        pathinfo = environ.get('PATH_INFO', '')
        if pathinfo.startswith("/"): pathinfo = pathinfo[1:]
        if pathinfo.endswith("/"): pathinfo = pathinfo[:-1]
        if pathinfo=="":
            start_response("302 ", [("location", "/index")])
            return []

        m = self._check_buildin_cmd(pathinfo, environ)
        if m!=None:
            start_response("200 ", [("content-type","application/json")])
            return [json.dumps(U(m), cls=JsonEncoder)]

        # 匹配路由
        app, func, args = self._find_entry(pathinfo, environ['REQUEST_METHOD'])
        if func != None:
            t = environ.get('REQUEST_METHOD', "")
            if t in getattr(func, "exposed", []):
                return self._run(environ, start_response, app, func, args)
        return self.application(environ, start_response)

