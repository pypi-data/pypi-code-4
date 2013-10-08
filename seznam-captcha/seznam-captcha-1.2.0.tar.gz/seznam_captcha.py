#!/usr/bin/python
# coding: utf-8


import urllib2

import requests


def create():
    return requests.get("http://captcha.seznam.cz/captcha.create").text

def image_url(key):
    return "http://captcha.seznam.cz/captcha.getImage?hash="+key

def audio_url(key):
    return "http://captcha.seznam.cz/captcha.getAudio?hash="+key

def check(key, text):
    if requests.get("http://captcha.seznam.cz/captcha.check?hash=%s&code=%s"%(key, text)).status_code == 200:
        return True
    return False


class Captcha:
    def __init__(self):
        self.key = create()
        self.image_file = None
        self.audio_file = None
        self.image_url = image_url(self.key)
        self.audio_url = audio_url(self.key)

    def get_image(self):
        if not self.image_file:
            self.image_file = urllib2.urlopen(self.image_url)
        return self.image_file

    def get_audio(self):
        if not self.audio_file:
            self.audio_file = urllib2.urlopen(self.audio_url)
        return self.audio_file

    def check(self, text):
        if not self.key:
            return False
        status = check(self.key, text)
        if self.image_file:
            self.image_file.close()
        if self.audio_file:
            self.audio_file.close()
        self.key = None
        self.image_file = None
        self.audio_file = None
        self.image_url = None
        self.audio_url = None
        return status