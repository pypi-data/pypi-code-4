#!/usr/bin/env python
# -*- coding: UTF-8 -*-

_BOARD_URL = "http://www.szu.edu.cn/board/read.asp"
_LOGIN_URL = "https://auth.szu.edu.cn/cas.aspx"
_CAPTCHA_URL = "https://auth.szu.edu.cn/gencheckcode.aspx"
_CAPTCHA_LOC = ".captcha.png"

import os

import requests
import lxml

from crszu import cr
from fetchurl import get_res
from errors import LoginFailError


def detect_network(fp=_BOARD_URL):
    """detect if is in Shenzhen University campus network.
    return True if so.
    """
    res = requests.get(fp, allow_redirects=False, verify=True)
    return res.status_code == requests.codes.ok


def get_captcha(session, cu=_CAPTCHA_URL, cl=_CAPTCHA_LOC):
    """get captcha image from url"""
    cp = session.get(_CAPTCHA_URL, verify=True)
    with open(cl, "wb") as f:
        f.write(cp.content)
    return cl


def login(uid, psw, lu=_LOGIN_URL, cu=_CAPTCHA_URL, cl=_CAPTCHA_LOC):
    """start auto login
    return requests.Session object if success, otherwise raise login error
    """
    s = requests.Session()

    tree = get_res(_LOGIN_URL, encoding="utf-8", session=s)
    __VIEWSTATE = tree.xpath("//*[@id=\"__VIEWSTATE\"]")[0].value
    __EVENTVALIDATION = tree.xpath("//*[@id=\"__EVENTVALIDATION\"]")[0].value

    for times in range(20):
        img = get_captcha(s)
        captcha = cr.captcha_regonize(img)
        os.remove(cl)
        podata = {"__VIEWSTATE": __VIEWSTATE,
                  "__EVENTVALIDATION": __EVENTVALIDATION,
                  "txtcardno": uid, "txtPass": psw, "txtCode": captcha,
                  "btnSubmit": u"登录"}
        r = s.post(_LOGIN_URL, data=podata, allow_redirects=False, verify=True)
        if r.status_code == 302:
            return s
    raise LoginFailError()
