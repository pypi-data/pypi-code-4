"""Parallel Python Software, Worker"""

# Author: Vitalii Vanovschi <support@parallelpython.com>,
#         Salvatore Masecchia <salvatore.masecchia@disi.unige.it>,
#         Grzegorz Zycinski <grzegorz.zycinski@disi.unige.it>
# License: new BSD.

import sys
import os
import StringIO
import cPickle as pickle

import pptransport

def preprocess(msg):
    fname, fsources, imports = pickle.loads(msg)
    fobjs = [compile(fsource, '<string>', 'exec') for fsource in fsources]
    for module in imports:
        try:
            if not module.startswith("from ") and not module.startswith("import "):
                module = "import " + module
            exec module
            globals().update(locals())
        except:
            print "An error has occured during the module import"
            sys.excepthook(*sys.exc_info())
    return fname, fobjs

class _WorkerProcess(object):

    def __init__(self):
        self.hashmap = {}
        self.e = sys.__stderr__
        self.sout = StringIO.StringIO()
        sys.stdout = self.sout
        sys.stderr = self.sout
        self.t = pptransport.CPipeTransport(sys.stdin, sys.__stdout__)
        self.t.send(str(os.getpid()))
        self.pickle_proto = int(self.t.receive())

    def run(self):
        try:
            #execution cycle
            while 1:
                __fname, __fobjs = self.t.creceive(preprocess)

                __sargs = self.t.receive()

                for __fobj in __fobjs:
                    try:
                        exec __fobj
                        globals().update(locals())
                    except:
                        print "An error has occured during the " + \
                              "function import"
                        sys.excepthook(*sys.exc_info())

                __args = pickle.loads(__sargs)

                __f = locals()[__fname]
                try:
                    __result = __f(*__args)
                except:
                    print "An error has occured during the function execution"
                    sys.excepthook(*sys.exc_info())
                    __result = None

                __sresult = pickle.dumps((__result, self.sout.getvalue()),
                        self.pickle_proto)

                self.t.send(__sresult)
                self.sout.truncate(0)
        except:
            print "A fatal error has occured during the function execution"
            sys.excepthook(*sys.exc_info())
            __result = None
            __sresult = pickle.dumps((__result, self.sout.getvalue()),
                    self.pickle_proto)
            self.t.send(__sresult)


if __name__ == "__main__":
        # add the directory with ppworker.py to the path
        sys.path.append(os.path.dirname(__file__))
        wp = _WorkerProcess()
        wp.run()
