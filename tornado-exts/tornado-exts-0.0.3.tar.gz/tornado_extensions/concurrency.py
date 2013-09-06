from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps

import tornado.ioloop
import tornado.web

MAX_WORKERS = 5

EXECUTOR = ThreadPoolExecutor(max_workers=MAX_WORKERS)


class ExecutorMixin(object):
    r"""Mixin class for decorator run_on_executor"""
    executor = EXECUTOR

    io_loop = tornado.ioloop.IOLoop.current()


def unblock(f):
    r"""Decorator responsible for executing http method in
    background by using thread pool from concurrent.futures lib."""

    @tornado.web.asynchronous
    @wraps(f)
    def wrapper(*args, **kwargs):

        self = args[0]

        def callback(future):
            self.write(future.result())
            self.finish()

        future = EXECUTOR.submit(
            partial(f, *args, **kwargs)
        )
        self.io_loop.add_future(
            future, lambda future: callback(future))

        return future
    
    return wrapper
