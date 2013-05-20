import sys
import traceback


def f():
    # print sys.exc_info()
    # print traceback.format_tb(sys.exc_info()[2])
    print traceback.format_exc()

try:
    1/0
except Exception as e:
    f()


f()