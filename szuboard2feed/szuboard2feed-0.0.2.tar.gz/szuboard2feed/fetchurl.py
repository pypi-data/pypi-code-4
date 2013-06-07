#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import requests
from lxml.html import fromstring
from lxml import etree
import times


def get_res(url, encoding=None, session=None):
    """
    return a etree of html text using given encoding type
    """
    session = session or requests.Session()
    res = session.get(url)
    res.encoding = encoding or res.encoding
    return fromstring(res.text)


def parse_readboard(tree):
    """
    return the root node of subhtml tree from xpath
    """
    xp = ("/html/body/div/center/table[2]/tr[1]/td/table/tr/td/table/tr[3]"
          "/td/table/tr[position()>2]/td[position()=4]//@href")
    return tree.xpath(xp)


def parse_notification(tree):
    """
    return str of title, time and content of each notification
    """
    title_xp = "/html/body/div/center/table/tr[3]/td/table/tr[1]/td//text()"
    time_xp = ("/html/body/div/center/table/tr[3]"
               "/td/table/tr[3]/td/table/tr/td[2]")
    content_xp = "/html/body/div/center/table/tr[3]/td/table/tr[2]/td"

    title = tree.xpath(title_xp)[0]
    time = tree.xpath(time_xp)[0].text[4:-1]
    time = times.format(times.to_universal(time, "Asia/Shanghai"), "UTC")
    content = etree.tostring(tree.xpath(content_xp)[0], encoding="unicode")
    return title, time, content
