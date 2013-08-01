# coding=utf-8

import time
import requests


def backoff_retry(retries=0, delay=1, backoff=2):
    """
        Based on: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

        In case of a connection error, will try to retry the function.

            retries: number of tries, can be 0
            delay:  sets the initial delay in seconds for the first try.
            backoff: factor used to increase the delay after new errors
    """
    if backoff <= 1:
        raise ValueError("backoff must be 0 or greater")
    if retries < 0:
        raise ValueError("retries must be greater than 0")
    if delay <= 0:
        raise ValueError("delay must be greater than 0")

    def wrapper(f):
        def retry_f(*args, **kwargs):
            try:
                return f(*args, **kwargs)  # first attempt
            except requests.ConnectionError:
                for t in range(retries):
                    try:
                        wait = delay * backoff * (t + 1)
                        time.sleep(wait)
                        return f(*args, **kwargs)  # new attempt
                    except requests.ConnectionError:
                        pass
                raise
        return retry_f
    return wrapper
