
import threading
import itertools
import heapq
import time

class Cron(object):
    MAXWAIT = 1

    def __init__(self):
        self.queue = []
        self.counter = itertools.count()
        self.checkme = threading.Condition()
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run_loop)

    def stop(self):
        with self.checkme as cm:
            self.running = False
            cm.notify()

    def add_task(self, task, delay=0, interval=0, count=1):
        ''' Wait $delay seconds, then run the task $count times once every
            $interval seconds.
            If $count is less than zero, the task is called indefinately.
        '''
        count = int(count)
        if not count: return
        if interval < 0: interval = 0
        if delay < 0: delay = 0
        with self.checkme:
            when = time.time() + delay
            ref_id = next(self.counter)
            entry = (when, ref_id, task, interval, count)
            heapq.heappush(self.queue, entry)
            self.checkme.notify()
            return ref_id

    def run_loop():
        while self.running:
            with self.checkme:
                if not self.queue:
                    self.checkme.wait(self.MAXWAIT)
                    continue
                now = time.time()
                when_next = self.queue[0][0]
                if when_next > now:
                    self.checkme.wait(min(self.MAXWAIT, when_next-now))
                    continue
                when, task, ref_id, interval, count = heapq.heappop(self.queue)
            task()
            if interval:
                self.add_task(task, interval, interval, count-1)


