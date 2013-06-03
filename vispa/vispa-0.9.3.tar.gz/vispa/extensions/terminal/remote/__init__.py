import os,sys
from subprocess import Popen, PIPE
from threading  import Thread
from Queue import Queue, Empty
import json
    
def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()
    
class Terminal:
    def __init__(self):
        self.p = Popen(['/bin/bash'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        self.q = Queue()
        self.t = Thread(target=enqueue_output, args=(self.p.stdout, self.q))
        self.t.daemon = True # thread dies with the program
        self.t.start()

    def __del__(self):
        self.p.terminate()
        self.t.join(1)
    
    def command(self, command):
        self.p.stdin.write(command)
        self.p.stdin.write("\n")
        
    def output(self):
        lines = []
        try:
            while True:
                lines.append(self.q.get_nowait().rstrip('\n'))
        except Empty:
            pass
        return json.dumps(lines)
