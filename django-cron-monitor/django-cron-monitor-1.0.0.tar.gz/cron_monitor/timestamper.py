# A simple python script that timestamps every line in stdin and prints it out
import time
import sys

for line in iter(sys.stdin.readline, ""):
    t = time.time()
    sys.stdout.write('%f %s' % (t, line))
