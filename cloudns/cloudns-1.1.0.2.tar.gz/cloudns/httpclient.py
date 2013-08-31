#!/usr/bin/env python
# coding=utf-8

"""abstracted httpclient. implemented using requests.

"""

import socket

import requests

from .utils import ok, error, fargs


def post(url, data):
    """try to POST URL with given data.

    Args:
        url: a url to fetch.
        date: a python dict, which will be encoded in
              application/x-www-form-urlencoded as message body.

    Return:
        {'ok': True, 'json': <python_dict>} on success.
        {'ok': False, 'msg': <error_msg>} on failure.

    """
    try:
        r = requests.post(url, data=data, verify=False)
        return ok(json=r.json())
    except ValueError as e:
        return error(msg=u'Expect json response, got %s' % (r.text,))
    except (requests.exceptions.RequestException, socket.error, IOError) as e:
        return error(msg=u'Request Exception: %s: %s' % (e.__class__.__name__,
                                                         fargs(e.args)))
