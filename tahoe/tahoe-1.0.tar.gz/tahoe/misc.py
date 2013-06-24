"""
The MIT License (MIT)

Copyright (c) 2013 Lunar Technology Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import base64
import datetime
from dateutil import parser as date_parser
import urlparse
import uuid


def cleanup_dict(d, keys=None):
    """
    Removes keys from the feed items that are not required to clients.
    """
    for k in keys:
        if k in d:
            del(d[k])


def get_timestamp(now=None, round=True):
    now = now or datetime.datetime.utcnow()
    timestamp = (now - datetime.datetime(1970, 1, 1)).total_seconds()
    if round:
        return int(timestamp)
    return timestamp


def timestamp_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp))


def date_string_to_datetime(date_string):
    return date_parser.parse(date_string)


def get_guid():
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).rstrip('=')


def normalize_email_address(raw_email_address):
    local_part, sep, domain_part = raw_email_address.partition('@')
    local_part_real, sep, local_part_plus = local_part.partition('+')
    # Google allows any number of dots in the name while all permutations point
    # to the same account.
    if domain_part == 'gmail.com':
        local_part_real = local_part_real.replace('.', '')
    return "{}@{}".format(local_part_real, domain_part)


def url_is_ok(suspect_url, valid_domain=None):
    if valid_domain:
        return (urlparse.urlparse(suspect_url).netloc in ('', valid_domain))
    return True
