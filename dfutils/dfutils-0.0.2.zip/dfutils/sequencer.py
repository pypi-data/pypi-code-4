import collections

from twisted.internet import defer
from twisted.python import failure

from branch import branch_df
from log import logsErrbacks


class QueueRunner(object):
    def __init__(self, f):
        self.f = f
        self.queue = defer.DeferredQueue()
        self._run()
    
    def put(self, *args, **kwargs):
        res_df = defer.Deferred()
        self.queue.put((res_df, args, kwargs))
        return res_df
    
    @logsErrbacks
    @defer.inlineCallbacks
    def _run(self):
        while True:
            res_df, args, kwargs = yield self.queue.get()
            func_df = defer.maybeDeferred(self.f, *args, **kwargs)
            #link the func's output to res_df
            func_df.addCallback(res_df.callback)
            func_df.addErrback(res_df.errback)
            #wait for the deferred without affecting its value
            try:
                yield branch_df(func_df)
            except:
                pass


def sequenced(keyf=lambda *args, **kwargs: None):
    """Make a decorator which sequences a function that returns deferreds.
    Function calls put a job on a queue, and the job is not run until all
    previous calls to the function have had their returned Deferreds fire.
    Optionally takes a function mapping function arguments to hashable objects
    used to key jobs, such that only jobs with the same key are sequenced.
    For example, if the keys are 'a' and 'b', then queueing two 'a' jobs will
    have them run in order, but queueing two 'a' jobs and one 'b' job will have
    the 'a' and 'b' job run at the same time.
    The wrapped function returns a deferred which fires with the result of the
    original function's deferred.
    """
    def wrapper(f):
        queue_runners = collections.defaultdict(lambda: QueueRunner(f))
        def wrapped(*args, **kwargs):
            queue_key = keyf(*args, **kwargs)
            return queue_runners[queue_key].put(*args, **kwargs)
        return wrapped
    return wrapper


def test():
    from twisted.internet import reactor, threads
    import time
    
    def slow_double(x):
        time.sleep(0.05)
        return x*2
    
    @defer.inlineCallbacks
    def dfdoubler(x):
        res = yield threads.deferToThread(slow_double, x)
        print "Just got %d * 2 = %d" % (x, res)
        defer.returnValue(res)
    
    sequenced_doubler = sequenced()(dfdoubler)
    keyed_sequenced_doubler = sequenced(lambda x: x >= 10)(dfdoubler)
    
    @sequenced()
    @defer.inlineCallbacks
    def throwError():
        yield defer.succeed(None)
        raise ValueError("HAH")
    
    @defer.inlineCallbacks
    def main():
        print "Unsequenced:"
        dfs = []
        for i in xrange(2, 30):
            dfs.append(dfdoubler(i))
        yield defer.DeferredList(dfs)
        
        print
        print "Sequenced and unkeyed:"
        dfs = []
        for i in xrange(2, 30):
            dfs.append(sequenced_doubler(i))
        yield defer.DeferredList(dfs)
        
        print
        print "Sequenced and keyed on >= 10:"
        dfs = []
        for i in xrange(2, 30):
            dfs.append(keyed_sequenced_doubler(i))
        yield defer.DeferredList(dfs)
        
        print
        print "With an error:"
        try:
            yield throwError()
        except Exception:
            import traceback
            print "Traceback:\n%s" % (traceback.format_exc(),)
        reactor.stop()
    
    main()
    reactor.run()

if __name__ == '__main__':
    test()