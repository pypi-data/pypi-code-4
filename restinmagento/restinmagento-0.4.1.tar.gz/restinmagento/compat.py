import sys

# True if we are running on Python 3.
PY3 = sys.version_info[0] == 3

if PY3:
    maxint = sys.maxsize
else:
    maxint = sys.maxint
    