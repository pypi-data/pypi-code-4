#!/usr/bin/env python
#-*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import time


def retry(f):
    def wrapper(*args, **nargs):
        timeout = 0.25
        num_tries = 5
        for tr in range(num_tries):
            try:
                return f(*args, **nargs)
            except:
                if tr == num_tries - 1:
                    raise
                time.sleep(timeout)
                timeout *= 2

    return wrapper

n = 0


def main():
    global n
    n += 1
    print('try:', n)
    assert 0

if __name__ == "__main__":
    retry(main)()
