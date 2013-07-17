from threading import Thread
from pika_simple_daemon.queue import Queue
import logging

class Daemon(object):

    def __init__(self, queue_params={}, logger=None):

        self._handlers = []
        self._threads = []
        self._queue_params = queue_params
        self._keep_running = True
        self._queue_class = Queue
        self._run_once = False
        if not logger:
            logger = logging.getLogger()
        self.logger = logger

    def add_handler(self, queue_name, callback, timeout=None,
                    finish_on_empty=False, limit=None,
                    finished_callback=None, routing_key="#",
                    queue_options={}, exchange_name=None):

        self._handlers.append(
            dict(
                queue_name=queue_name,
                callback=callback,
                timeout=timeout,
                finish_on_empty=finish_on_empty,
                limit=limit,
                finished_callback=finished_callback,
                queue_options=queue_options,
                exchange_name=exchange_name,
                routing_key=routing_key
            )
        )

    def run(self):
        try:
            for handler in self._handlers:
                self.logger.warn("Starting a thread for {0}".format(handler['queue_name']))
                thread = Thread(target=self._receive, name=handler['queue_name'], kwargs=handler)
                thread.daemon=False
                thread.start()
                thread.join(1)
                self._threads.append(thread)
        except KeyboardInterrupt:
            self.kill()


    def kill(self):
        self._keep_running = False

    def _receive(self, *args, **kwargs):
        queue = self._queue_class()
        queue.connect(self._queue_params)
        while self._keep_running is True:
            queue.receive(**kwargs)
            if self._run_once is True:
                return


