#!/usr/bin/env python3

"""See the docstring of SafeInterruptHandler.
Works with python3 as well.

Uploaded to https://gist.github.com/4006374
"""

__author__ = 'Arpad Horvath'

import signal
import functools
try:
    import urllib.request
except ImportError:
    import urllib
import os
import sys

def decorator(d):
    "Make function d a decorator: d wraps a function fn. @author Darius Bacon"
    return lambda fn: functools.update_wrapper(d(fn), fn)
decorator = decorator(decorator)

class SafeInterruptHandler(object):
    """Handle interrupt in critical cases.

    SafeInterruptHandler.on()
    and
    SafeInterruptHandler.off()
    you can switch on and off the special working.

    You can create a safe function with the
    @SafeInterruptHandler.decorator
    decorator.
    """
    finish = False

    @classmethod
    def signal_handler(cls, signal, frame):
        cls.finish = True

    @classmethod
    def on(cls):
        signal.signal(signal.SIGINT, cls.signal_handler)

    @classmethod
    def off(cls):
        signal.signal(signal.SIGINT, signal.default_int_handler)

    @classmethod
    def decorator(cls, fn):
        def fn_(*args, **kwargs):
            cls.on()
            fn(*args, **kwargs)
            cls.off()
            if cls.finish:
                sys.exit(1)
        return fn_


urlretrieve = urllib.urlretrieve if "urlretrieve" in dir(urllib) else urllib.request.urlretrieve

@SafeInterruptHandler.decorator
def download_files(files, baseurl, path="."):
    if not baseurl[-1] == "/":
        baseurl += "/"
    if isinstance(files, str):
        files = [files]
    for file_ in files:
        urlretrieve("".join([baseurl, file_]),
                        os.path.join(path, file_))

def test():
    while True:
        print("S")
        download_files("splash_eu.jpg", "http://bocs.eu")

if __name__ == "__main__":
    test()
