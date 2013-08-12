# -*- coding: utf-8 -*-
from random import choice
from sample_data_utils.text import text


def email(*tlds):
    domains = tlds or ['example.org']
    return ("%s.%s@%s" % (text(10), text(10), choice(domains))).lower()
