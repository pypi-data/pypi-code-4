from __future__ import with_statement

import sys
import signal
import time

def ignore(sig, frame):
    pass

signal.signal(signal.SIGTERM, ignore)

if len(sys.argv) > 1:
    with open(sys.argv[1], "w") as outf:
        outf.write("signal set up")

while True:
    try:
        time.sleep(.1)
    except KeyboardInterrupt:
        pass
