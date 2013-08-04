"""
Collection of various compatibility functions for 2/3 compatibility from various
projects that aren't included in future or six:
- Django
- Gevent
"""

# From https://bitbucket.org/damoxc/gevent-py3/raw/06d1edc2dfbc281b59114e5b29a132106fc895d4/gevent/compat.py

# Create a raise_ method that allows re-raising exceptions with the cls
# value and traceback on Python2 & Python3.
if sys.version_info < (3, 0):
    exec ("""def raise_(cls, val=None, tb=None):
    raise cls, val, tb""")
else:
    exec ("""def raise_(cls, val=None, tb=None):
    raise val.with_traceback(tb)""")
__builtins__['raise_'] = raise_

# Also grab useful functions from here: https://github.com/django/django/blob/master/django/utils/encoding.py
