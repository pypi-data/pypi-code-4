#!/usr/bin/env python

"""
expand a URL under ROOT.
"""

import sys
from whiff import resolver

ENV = {
    "CONTENT_LENGTH" : "",
    "CONTENT_TYPE" : "text/plain",
    "GATEWAY_INTERFACE" : "CGI/1.1",
    "HOME" : "/Users/Aaron",
    "HTTP_ACCEPT" : "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
    "HTTP_ACCEPT_CHARSET" : "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
    "HTTP_ACCEPT_ENCODING" : "gzip,deflate",
    "HTTP_ACCEPT_LANGUAGE" : "en-us,en;q=0.5",
    "HTTP_CONNECTION" : "keep-alive",
    "HTTP_COOKIE" : "skimpycookie=1231280424.69; JSESSIONID=5e9331b4-f3af-4f6c-9a17-7a7375b3e051.localhost; UserInfo=INVALIDUSER/INVALIDPASSWORD",
    "HTTP_HOST" : "localhost:8888",
    "HTTP_KEEP_ALIVE" : "300",
    "HTTP_REFERER" : "http://localhost:8888/misc/test_ifcgi",
    "HTTP_USER_AGENT" : "Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en-US; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14",
    "PATH_INFO" : "/misc/test_ifcgi",
    "QUERY_STRING" : "",
    "REMOTE_ADDR" : "127.0.0.1",
    "REMOTE_HOST" : "localhost",
    "REQUEST_METHOD" : "GET",
    "SCRIPT_NAME" : "",
    "SECURITYSESSIONID" : "b144e0",
    "SERVER_NAME" : "localhost",
    "SERVER_PORT" : "8888",
    "SERVER_PROTOCOL" : "HTTP/1.1",
    "SERVER_SOFTWARE" : "WSGIServer/0.1 Python/2.5",
    "wsgi.url_scheme" : "http"
    }

def start_response(*args):
    pass

DEFN = """
def f():
    import %s
    return %s
"""
def getRootModule(root):
    if root.endswith("/"):
        root = root[:-1]
    defn = DEFN % (root, root)
    #pr "exec", defn
    exec(defn)
    rootModule = f()
    return rootModule

def expand(root, url):
    env = ENV.copy()
    env["PATH_INFO"] = url
    rootModule = getRootModule(root)
    rootApplication = resolver.moduleRootApplication("/", rootModule,
                                                     exception_middleware=None,
                                                     on_not_found=None, # show traceback (could comment)
                                                     )
    result = list( rootApplication(env, start_response))
    return "".join(result)

if __name__=="__main__":
    sys.path.insert(0, ".")
    #pr sys.path
    print expand(*sys.argv[1:])
