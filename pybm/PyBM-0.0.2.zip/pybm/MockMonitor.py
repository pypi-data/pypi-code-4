import threading
import time
import random
from pyBM.Job import Status
from pyBM import Job


class MockMonitor():
    def __init__(self):
        self.job_list = []
        self.job_list.append(Job('A name', Status.ERROR, 50))

    def get_job_list(self):
        return self.job_list

    def start(self):
        self.alive = True
        self.thread = threading.Thread(target=self.run)
        self.thread.setDaemon(True)
        self.thread.start()

    def run(self):
        while self.alive:
            state = random.randint(1, 5)
            if state == 1:
                state = Status.OK
            elif state == 2:
                state = Status.WARNING
            elif state == 3:
                state = Status.ERROR
            elif state == 4:
                state = Status.UNKNOWN
            elif state == 5:
                state = Status.BUILDING

            self.job_list.append(Job('A name', state, 100))
            time.sleep(1)

    def stop(self):
        self.alive = False
