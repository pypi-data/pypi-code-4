#!/usr/bin/python
#coding=utf-8
import config


def func(arg):
    if arg not in set([u'help', u'man']):
        return arg
    else:
        return config.HELP_RES
