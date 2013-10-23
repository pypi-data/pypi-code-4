#coding: utf-8
__docformat__="epytext"

import cgi, urlparse, Cookie
import dateutil.parser
from decimal import Decimal
import types

class HttpRequest(object):
    """HTTP请求对象"""

    def __init__(self, env, fp):
        """@param env: 环境变量
           @type env: dict
           @param fp: 数据文件
           @type fp: fileobject"""
        self.env = env
        self.params = {}
        self.upload = None
        self.fread = fp

        fp.seek(0)
        fs = cgi.FieldStorage(fp=fp, environ=env, keep_blank_values=1)
        if fs.list==None:
            self.upload = fs.file
            lst = [cgi.MiniFieldStorage(k, v) for k, v in urlparse.parse_qsl(env.get("QUERY_STRING",""), keep_blank_values=1)]
        else:
            lst = fs.list

        d = {}
        for f in lst:
            if f.file!=None:
                self.upload = f.file
            if f.name in d:
                d[f.name].append(f.value)
            else:
                d[f.name] = [f.value]
        self.params = d

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
        """读取参数值
           @param name: 参数名
           @type name: string
           @keyword default: 默认值
           @rtype: string"""
        if name in self.params:
            v = self.params[name]
            if type(v) in (types.ListType, types.TupleType):
                return v[-1] 
            else:
                return v
        else:
            return default

    def getint(self, name, default=0):
        """读取整数参数值
           @param name: 参数名
           @type name: string
           @keyword default: 默认值
           @rtype: int"""
        try:
            return int(self.get(name, default))
        except:
            return default

    def getfloat(self, name, default=0.0):
        "读取浮点数"
        try:
            v = self.get(name, default)
            assert str(v) not in ('NaN', 'nan')
            return float(v)
        except:
            return default

    def getnum(self, name, default=Decimal('0')):
        """读取Decimal
           @param name: 参数名
           @type name: string
           @keyword default: 默认值
           @rtype: float"""
        try:
            v = self.get(name, default)
            assert str(v).lower()!="nan"
            return Decimal(v)
        except:
            return default

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

    def _os_type(self):
        """终端操作系统类型
            @return: 'android' | 'ipad' | 'iphone' | ''
            @rtype: string"""
        ua = self.env.get("USER-AGENT","").lower()
        for k in ('android', 'ipad', 'iphone'):
            if k in ua:
                return k
        return ""
    ostype = property(_os_type)

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

