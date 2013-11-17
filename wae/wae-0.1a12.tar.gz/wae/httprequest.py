#coding: utf-8
__docformat__="epytext"

import cgi, urlparse, Cookie
import dateutil.parser
from decimal import Decimal
import types, sys, os

class HttpRequest(object):
    """HTTP请求对象"""

    def __init__(self, env=os.environ, fp=sys.stdin):
        """@param env: 环境变量
           @type env: dict
           @param fp: 数据文件
           @type fp: fileobject"""
        self.env = env
        self.params = {}
        self.upload = None
        self.fread = fp

        if fp != sys.stdin: fp.seek(0)
        fs = cgi.FieldStorage(environ=env, fp=fp, keep_blank_values=1)
        if fs.list==None:
            self.upload = fs.file
            lst = [cgi.MiniFieldStorage(k, v) for k, v in urlparse.parse_qsl(env.get("QUERY_STRING",""), keep_blank_values=1)]
        else:
            lst = fs.list

        self.params = {}
        for f in lst:
            if f.file!=None:
                self.upload = f.file

            if f.name.endswith("[]"):
                n = f.name[:-2]
            else:
                n = f.name

            if n in self.params:
                self.params[n].append(f.value)
            else:
                self.params[n] = [f.value]


    def keys(self):
        """返回参数名列表"""
        return self.params.keys()

    def has_key(self, name):
        """检测给定的参数名是否存在"""
        return self.params.has_key(name)

    def geta(self, name, default=[]):
        """读取参数数组
           @param name: 参数名
           @type name: string
           @keyword default: 默认值
           @rtype: string[]"""
        return self.params.get(name, default)

    def get(self, name, default=None):
        """返回参数值
           @param name: 参数名
           @type name: string
           @keyword default: 默认值
           @rtype: string or string[]"""
        if name in self.params:
            v = self.params[name]
            assert type(v)==types.ListType, v
            if len(v)==1:
                return v[0]
            else:
                return v
        else:
            return default

    def _convert(self, src, failover, func):
        if type(src) in (types.ListType, types.TupleType):
            res = []
            for x in src:
                try:
                    res.append(func(x))
                except:
                    res.append(failover)
        elif isinstance(src, (types.StringType, types.IntType, types.FloatType)):
            try:
                res = func(src)
            except:
                res = failover
        elif src==None:
            res = None
        else:
            assert False, (src, type(src), func)
        return res

    def getint(self, name, default=0):
        "读取整数参数值"
        return self._convert(self.get(name, default), default, int)

    def getfloat(self, name, default=0.0):
        "读取浮点数"
        return self._convert(self.get(name, default), default, float)

    def getnum(self, name, default=Decimal('0')):
        "读取Decimal"
        res = []
        for v in self._convert(self.get(name, default), default, Decimal):
            if str(v)=="nan": v = default
            res.append(v)
        return res

    def getbool(self, name, default=False):
        """读取bool参数值
           I{true,t,y,yes,1}对应于B{True}, I{false,f,n,no,0}对应于B{False}. 不能识别的返回I{default}.
           @param name: 参数名
           @type name: string
           @keyword default: 默认值
           @rtype: bool"""
        v = self.get(name, default)
        if v in (None, True, False): return v

        v = str(v).lower()
        if v in ("1","t","y","true","yes"):
            return True
        elif v in ("0","f","n","false","no"):
            return False
        else:
            return default

    def getdate(self, name, default=None):
        """读取日期参数值
           @param name: 参数名
           @type name: string
           @keyword default: 默认值
           @rtype: datetime.date"""
        v = self.get(name, "").strip()
        if v!="":
            try:
                return dateutil.parser.parse(v)
            except:
                return default
        else:
            return default

    def getfile(self, name):
        """返回上传的文件对象
           @param name: 文件的参数名
           @rtype: FileObject | None"""
        if name in self.params:
            return self.params[name].file
        else:
            return None

    def _get_cookies(self):
        return Cookie.SimpleCookie(self.env.get('HTTP_COOKIE', ''))
    cookies = property(_get_cookies)

    def _is_ajax(self):
        """是否AJAX请求"""
        t0 = self.env.get('X-REQUESTED-WITH','').lower()
        t1 = self.env.get('X_REQUESTED_WITH','').lower()
        t2 = self.env.get('HTTP_X_REQUESTED_WITH','').lower()
        return 'xmlhttprequest' in (t0, t1, t2)
    is_ajax = property(_is_ajax)

    def _get_req_method(self):
        return self.env.get("REQUEST_METHOD")
    method = property(_get_req_method)

