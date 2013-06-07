#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import gevent
from lxml import etree

from fetchurl import parse_readboard, parse_notification, get_res
from genfeednode import generate_meta, generate_entry
from autologin import login, detect_network

_URL_PREFIX = "http://www.szu.edu.cn/board/"
_BOARD = "read.asp"
_ENCODING = "GBK"
_FILE_PATH = "atom.xml"


def generate_root(s=None):
    """build root from web page."""
    url_surfixs = parse_readboard(get_res(_URL_PREFIX+_BOARD, _ENCODING, s))
    root = generate_meta()
    return root, url_surfixs


def generate_body(root, surfix, s=None):
    """build the entry node from web page."""
    t, u, c = parse_notification(get_res(_URL_PREFIX + surfix, _ENCODING, s))
    entry = generate_entry(t, u, c, _URL_PREFIX + surfix)
    root.append(entry)
    return root


def write_atom(root, fp=_FILE_PATH):
    """write atom tree to xml."""
    et = etree.ElementTree(root)
    with open(fp, "wb") as output_file:
        et.write(output_file, encoding="unicode")


def get_feed(items=None, uid=None, psd=None):
    """get feed element tree root."""
    session = None
    if False == detect_network():
        session = login(uid, psd)
    root, urls = generate_root(session)
    if items is not None:
        urls = urls[:items]
    events = [gevent.spawn(generate_body, root, url, session) for url in urls]
    gevent.joinall(events)
    return root


def generate_feed(fp=_FILE_PATH, items=None, uid=None, psd=None):
    """generate feed file."""
    root = get_feed(items, uid, psd)
    write_atom(root, fp)
