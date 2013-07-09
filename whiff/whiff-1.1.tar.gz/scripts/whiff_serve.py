#!/usr/bin/env python

"""
Serve whiff root directory
"""

import sys
from whiff import resolver
from whiff.resources import inMemorySession
from whiff.resources import FreshName
from whiff.middleware import displayTraceback
import wsgiref.simple_server

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

def serve(root, port=8888, host='localhost'):
    rootModule = getRootModule(root)
    sessionFinder = inMemorySession.memorySessionFinder(timeout=600) # 10 minute timeout
    profileFinder = inMemorySession.memoryProfileFinder()
    namefinder = FreshName.FreshNameFinder()
    rootApplication = resolver.moduleRootApplication("/", rootModule,
                                                     exception_middleware=displayTraceback.__middleware__,
                                                     #on_not_found=None, # show traceback (could comment)
                                                     )
    rootApplication.registerResourceFinder(prefix="session", finder=sessionFinder)
    rootApplication.registerResourceFinder(prefix="profile", finder=profileFinder)
    rootApplication.registerResourceFinder(prefix="freshName", finder=namefinder)
    port = int(port)
    srv = wsgiref.simple_server.make_server(host, port, rootApplication)
    print "serving whiff root", rootModule
    print "as http on host", host, "port", port
    srv.serve_forever()

if __name__=="__main__":
    sys.path.insert(0, ".")
    #pr sys.path
    print serve(*sys.argv[1:])
