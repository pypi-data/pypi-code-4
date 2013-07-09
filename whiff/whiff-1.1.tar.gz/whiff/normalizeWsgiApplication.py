"""
The WSGI spec requires the start_response to return a write(bytes) function.
This wrapper catches calls to write and dispatches them to the iterable
so that the rest of WHIFF doesn't have to deal with calls to write().
"""

import types
import stream

class Collect_start_response:
    "collect any calls to write() result of start_response"
    def __init__(self, inner_start_response):
        self.inner_start_response = inner_start_response
        self.writes = []
    def __call__(self, status, headers):
        sr = self.inner_start_response
        # make sure the headers are bytes, not unicode
        headers = [ (stream.mystr(n), stream.mystr(v)) for (n,v) in headers ]
        status = stream.mystr(status)
        sr(status, headers)
        return self.write_collector
    def write_collector(self, s):
        self.writes.append(s)
    def dump_writes(self):
        L = self.writes
        if L:
            self.writes = []
        return L

def normalize(wsgi_application, env, start_response):
    """
    Evaluate the application and
    catch any calls to write() and put them in iterable response
    """
    collector = Collect_start_response(start_response)
    app_result = wsgi_application(env, collector)
    # optimized path for list or tuple result
    result_type = type(app_result)
    if result_type in (types.ListType, types.TupleType):
        #pr "got", result_type
        dump = collector.dump_writes()
        # I guess the dump should go before the iterable???
        if dump:
            if app_result:
                #pr "catenating", len(dump), len(app_result)
                return dump + list(app_result)
            else:
                #pr "returning only calls to write"
                return dump
        else:
            #pr "returning app_result sequence"
            return app_result
    else:
        # interleave calls to write() with the iterable
        #pr "interleaving iterable and write() calls"
        return interleave_results(app_result, collector)

def interleave_results(app_result, collector):
    """
    yield elements in app_result prefixed by any strings captured by calls to collector.write_collector
    """
    for chunk in app_result:
        for write_chunk in collector.dump_writes():
            #pr "yielding write", repr(write_chunk)
            yield write_chunk
        #pr "yielding element", repr(chunk)
        yield chunk
    # any calls to write after last element?
    for write_chunk in collector.dump_writes():
        yield write_chunk
        
###= testing stuff...
def wsgi_test_application1(env, start_response):
    write_function = start_response("200 OK", [('Content-Type', 'text/plain')])
    yield "first line\n"
    write_function("second line\n")
    yield "third line\n"
    write_function("last line\n")

def wsgi_test_application2(env, start_response):
    write_function = start_response("200 OK", [('Content-Type', 'text/plain')])
    write_function("first line\n")
    write_function("second line\n")
    return ["last line\n"]

def ignore_start_response(*whatever):
    return None

def test_app(app):
    env = {}
    result = normalize(app, env, ignore_start_response)
    #pr "normalize returns", type(result), result
    L = list(result)
    return "".join(L)

if __name__=="__main__":
    print "normalizing", wsgi_test_application1
    print test_app(wsgi_test_application1)
    print "normalizing", wsgi_test_application2
    print test_app(wsgi_test_application2)
