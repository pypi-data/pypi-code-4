import Queue
import threading

try:
    from raven.contrib.django.models import client as sentry_client
    error_report = sentry_client.create_from_exception
except ImportError:
    error_report = lambda: None

_background_thread = None

def queue(fn, *args, **kwargs):
    '''
    Queues up a function call to run in a background thread to ensure that
    performance is not impacted by calls to other services.

    Whilst a good attempt is made, this does NOT guarantee execution. Use a
    proper queueing system for that.

    As an example, this is good for internal counters that can be safely
    inaccurate by a few counts.
    '''
    _queue(fn, *args, **kwargs)

# Private function allows us to patch in tests
def _queue(fn, *args, **kwargs):
    global _background_thread
    if not _background_thread:
        _background_thread = BackgroundThread()
        _background_thread.start()
    _background_thread.queue.put((fn, args, kwargs))

def terminate(wait=False):
    if _background_thread:
        _background_thread.terminate.set()
        if wait:
            _background_thread.join()

# Useful for clearing before tests
def _clear_and_terminate():
    if not _background_thread:
        return
    while True:
        try:
            _background_thread.queue.get_nowait()
        except Queue.Empty:
            break
    terminate(wait=True)

class BackgroundThread(threading.Thread):

    def __init__(self):
        super(BackgroundThread, self).__init__()
        self.parent_thread = threading.current_thread()
        self.queue = Queue.Queue()
        self.terminate = threading.Event()

    def run(self):
        while not self.terminate.is_set() and self.parent_thread.is_alive():
            try:
                fn, args, kwargs = self.queue.get(True, 0.2)
                try:
                    fn(*args, **kwargs)
                except:
                    error_report()
            except Queue.Empty:
                continue
        global _background_thread
        _background_thread = None
