from tornado import gen, ioloop
from tornado.concurrent import Future
import datetime
import functools

def set_future_result(future):
    future.set_result("NICE")

def callback(future):
    print "callback executed"

def get_future():
    f = Future()
    iol = ioloop.IOLoop.current()
    iol.add_future(f, callback)
    iol.add_timeout(datetime.timedelta(seconds=5), functools.partial(set_future_result, f))
    return f

@gen.coroutine
def wait_for_future():
    res = yield get_future()
    print res, "yeapp"


loop = ioloop.IOLoop.instance()
loop.add_timeout(datetime.timedelta(seconds=1), wait_for_future)
loop.start()

