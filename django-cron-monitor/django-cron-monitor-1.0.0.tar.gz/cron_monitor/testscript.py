import time
import sys

for i in range(2):
    time.sleep(1)
    sys.stdout.write('Printing this ')
    sys.stdout.write('to stdout%d\n' % i)

time.sleep(2)
sys.stderr.write('Boo')

sys.stderr.write('hifhsuiofjn')

for i in range(3):
    sys.stderr.write('Printing <>\'\"&/ this to stderr%d\n' % i)
