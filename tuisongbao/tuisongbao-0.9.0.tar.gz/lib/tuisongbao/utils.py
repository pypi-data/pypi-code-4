#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil import tz
import hashlib

TIMEZONE_SHANGHAI = tz.gettz('Asia/Shanghai')
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
EAST_EIGHT_TIMEZONE = 28800


def formatDatetime(dt=datetime.now(tz.tzlocal())):
    if dt.tzinfo is None:
        dt = datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond, tz.tzlocal())

    return dt.astimezone(TIMEZONE_SHANGHAI).strftime(DATETIME_FORMAT)


def md5_sign(params, secret):
    sorted_keys = sorted(params.keys())
    str_to_sign = secret
    for key in sorted_keys:
        str_to_sign += key + params[key]
    str_to_sign += secret
    str_to_sign = str_to_sign.encode('utf-8')

    return hashlib.md5(str_to_sign).hexdigest().upper()
