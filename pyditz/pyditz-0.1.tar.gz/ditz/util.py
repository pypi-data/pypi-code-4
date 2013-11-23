"""
Utility functions.
"""

import os
import re
import yaml
import socket
from datetime import datetime


def read_yaml_file(path):
    """
    Read YAML data from a file.
    """

    with open(path) as fp:
        return read_yaml(fp)


def read_yaml(fp):
    """
    Read YAML data from a stream.
    """

    return yaml.safe_load(fp)


def age(date):
    """
    Return a human-readable in-the-past time string given a date.
    """

    return ago((datetime.now() - date).total_seconds())


def ago(counter):
    """
    Return how long ago a number of seconds is.
    """

    counter = int(counter)
    if counter == 0:
        return "now"

    for unit, count in (("second", 60),
                        ("minute", 60),
                        ("hour",   24),
                        ("day",     7),
                        ("week",    4),
                        ("month",  12),
                        ("year",    0)):
        if count > 0 and counter >= count * 2:
            counter /= count
        else:
            break

    return "%d %s%s" % (counter, unit, "s" if counter > 1 else "")


def extract_username(email):
    """
    Return a short user name given email text.
    """

    if '@' not in email:
        return email

    m = re.search('([A-Za-z0-9_.]+)@', email)
    if m:
        return m.group(1)

    return email


def default_name():
    """
    Return a default user name.
    """

    for var in "DITZUSER", "USER", "USERNAME":
        if var in os.environ:
            return os.environ[var]

    return "ditzuser"


def default_email():
    """
    Return a default email address.
    """

    return default_name() + '@' + hostname()


def hostname():
    """
    Return the host name.
    """

    for var in "DITZHOST", "HOSTNAME", "COMPUTERNAME":
        if var in os.environ:
            return os.environ[var]

    try:
        return socket.gethostname()
    except socket.error:
        return "UNKNOWN"


def print_columns(items, linelen=70, spacing=2):
    """
    Print a number of items in column format.
    """

    maxlen = max(len(text) for text in items)
    columns = max(linelen / (maxlen + spacing), 1)
    padding = " " * spacing

    count = 0
    while count < len(items):
        print items[count].ljust(maxlen) + padding,
        count += 1
        if count % columns == 0:
            print

    if count % columns != 0:
        print


def error(*args):
    """
    Give a Ditz error.
    """

    print "Error: " + " ".join(map(str, args))


class DitzError(Exception):
    "A generic Ditz error."
