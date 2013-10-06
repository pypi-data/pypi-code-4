#!/usr/bin/python
# coding: utf-8


import requests


def create():
    return requests.get("http://captcha.seznam.cz/captcha.create").text

def image_url(key):
    return "http://captcha.seznam.cz/captcha.getImage?hash="+key

def check(key, text):
    if requests.get("http://captcha.seznam.cz/captcha.check?hash=%s&code=%s"%(key, text)).status_code == 200:
        return True
    return False
