#coding: utf-8
import os, sys, traceback, types, json
import wae.utils
from wae.httprequest import HttpRequest
from wae.httpresponse import HttpResponse
from wae.session import RedisSession
from wae.middleware import JsonEncoder
import Cheetah.Template
from wae.utils import exposed


class CommandSet(object):
    "CGI程序集对象"
    SESSION_COOKIE_NAME   = ""  # session cookie
    TEMPLATE_ROOT_PATH = ""  # template root path

    def __init__(self, req, res):
        assert isinstance(req, HttpRequest), req
        assert isinstance(res, HttpResponse), req
        self.request = req
        self.response = res

    def get_session(self, domain=""):
        """取得session对象"""
        if self.SESSION_COOKIE_NAME=="":
            return None

        ck = self.request.cookies.get(self.SESSION_COOKIE_NAME)
        if ck != None:
            sessid = ck.value
        else:
            sessid = self.request.get(self.SESSION_COOKIE_NAME, "").strip()
            if sessid == "": 
                sessid = None

        rdb = wae.connect.connect_redis()
        sess = RedisSession(rdb, sessid=sessid, domain=domain)
        if sess.is_new:
            self.response.set_cookie(self.SESSION_COOKIE_NAME, sess.sessid)
        return sess


    def beforeRun(self):
        "执行备前"
        return True

    def afterRun(self):
        "执行善后"
        pass

    def get_template_root_path(self):
        "返回模板根路径"
        return self.TEMPLATE_ROOT_PATH

    def render(self, name):
        "渲染页面"
        tmpls = self.get_templates(name, self.get_template_root_path())
        for fn in tmpls:
            if os.path.exists(fn) and not os.path.isdir(fn):
                fh = open(fn)
                text = fh.read()
                fh.close()
                text = "#encoding utf-8\n%s" % text

                tcls = Cheetah.Template.Template.compile(source=text)
                a = tcls(searchList=[{"response":self.response, "request":self.request}])
                return str(a)
        return "template missing: %s"  % ", ".join(tmpls)


    @classmethod
    def get_templates(cls, tmplname, rootpath):
        "视图模板文件"
        if rootpath.endswith("/"): rootpath = rootpath[:-1]

        if cls == CommandSet:
            if rootpath!="":
                return ["%s/%s.tmpl" % (rootpath, tmplname)]
            else:
                return [tmplname]

        else:
            if rootpath!="":
                lst = ["%s/%s/%s.tmpl" % (rootpath, cls.__name__, tmplname)]
            else:
                lst = ["%s/%s.tmpl" % (cls.__name__, tmplname)]

            for t in cls.__bases__[0].get_templates(tmplname, rootpath):
                if not t in lst:
                    lst.append(t)

            return lst


    @classmethod
    def run(cls, cmd, req, res, *args, **kwargs):
        if req==None: req = HttpRequest()
        if res==None: res = HttpResponse()

        if hasattr(cls, cmd):
            f = getattr(cls, cmd)
            if getattr(f, "exposed", None)!=None:
                if req.method in getattr(f, "exposed"):
                    a = cls(req, res)
                    if a.beforeRun():
                        ret = getattr(a, cmd)(*args, **kwargs)
                        if ret==None: ret = a.render(f.__name__)
                        a.afterRun()
                    else:
                        ret = ""
                    return ret

        raise Exception("Unkown command '%s'" % cmd)


def run(pathinfo="", classpath="", env=os.environ, stdout=sys.stdout, **kwargs):
    "执行CGI"
    if pathinfo == "":
        pathinfo = os.environ['PATH_INFO']

    if pathinfo.startswith("/"): 
        pathinfo = pathinfo[1:]

    a = pathinfo.split(":", 1)
    cmd = a[0].replace("-", "_")
    if len(a)>1:
        args = a[1].split(",")
    else:
        args = []

    a = cmd.split(".", 1)
    modname = a[0].replace("/", ".")
    if classpath != "":
        modname = "%s.%s" % (classpath, modname)

    if len(a)>1:
        method = a[1].replace(".", "_")
    else:
        method = "index"

    req = HttpRequest()
    res = HttpResponse()
    res.set_header("content-type", "text/html;charset=utf-8")

    try:
        mod = __import__(modname, fromlist=[''])
        clsname = modname.split(".")[-1]
        cls = getattr(mod, clsname)
        assert issubclass(cls, CommandSet), cls
        ret = cls.run(method, req, res, *args, **kwargs)

    except:
        msg = traceback.format_exception(*sys.exc_info())
        msg.append(modname)
        msg.append("")
        sys.stderr.write("\n".join(msg))

        stdout.write("Status: 500\n")
        stdout.write("Content-Type: text/plain;charset=utf-8\n")
        stdout.write("\n")
        stdout.write("Internal Server Error\n")

        return -1

    # write response
    stdout.write("Status: %.3d\n" % res.status)
    for k, v in res.headers.items():
        stdout.write("%s: %s\n" % (k, v))
    stdout.write("\n")

    if type(ret)==types.StringType:
        out = ret
    elif type(ret)==types.UnicodeType:
        out = ret.encode("utf-8")
    elif hasattr(ret, "read"):
        # file-like object
        ret.seek(0)
        out = FileWrapper(ret)
    else:
        out = json.dumps(wae.utils.U(ret), cls=JsonEncoder)
        if req.get("callback", "")!="":
            out = "%s(%s)" % (req.get("callback"), out)

    stdout.write(out)
    return 0

