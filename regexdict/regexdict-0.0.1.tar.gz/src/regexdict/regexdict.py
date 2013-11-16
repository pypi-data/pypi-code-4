#!/usr/bin/env python
#coding=utf-8

import re


class RegexDict(object):

    def __init__(self):
        self.words = []

    def get_defination(self, word):
        try:
            defination = self.words[word]
        except KeyError:
            defination = ''
        return defination

    def regexquery(self, regex, words):
        r = re.compile(regex)
        match_words = filter(r.match, self.words)
        return match_words

    def get_dictcn(self, word):
        pass

    def get_youdaodict(self, word):
        pass

    def get_baidudict(self, word):
        pass

    def get_bingdict(self, word):
        pass
