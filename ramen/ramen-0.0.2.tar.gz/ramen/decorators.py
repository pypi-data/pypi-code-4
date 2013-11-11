
import functools
import greenlet
from tornado.concurrent import Future

def asynchronize(loop):

    def sub_asynchronize(sync_method):
        
        @functools.wraps(sync_method)
        def method(*args, **kwargs):
            callback = kwargs.pop('callback', None)

            if callback:
                if not callable(callback):
                    raise callback_type_error
                future = None
            else:
                future = Future()

            def call_method():
                # Runs on child greenlet
                # TODO: ew, performance?
                try:
                    result = sync_method(*args, **kwargs)
                    if callback:
                        # Schedule callback(result, None) on main greenlet
                        loop.add_callback(functools.partial(
                            callback, result))
                    else:
                        # Schedule future to be resolved on main greenlet
                        loop.add_callback(functools.partial(
                            future.set_result, result))
                except Exception, e:
                    if callback:
                        loop.add_callback(functools.partial(
                            callback, e))
                    else:
                        loop.add_callback(functools.partial(
                            future.set_exception, e))

            # Start running the operation on a greenlet
            greenlet.greenlet(call_method).switch()
            return future

        return method
    return sub_asynchronize