#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.conf.urls import patterns, url

urlpatterns = patterns('',

    # Android API
    url(r'^/?$', 'fondasms.views.fondasms_handler',
        name='fondasms'),

    # in-browser tester
    url(r'^tester/?$', 'fondasms.views.fondasms_tester',
        name='fondasms_tester'),
)
