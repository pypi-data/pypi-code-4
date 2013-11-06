#!/usr/bin/env python
# -*- coding: utf-8 -*-

from notmm.utils.YAMLDct import YAMLDct

__all__ = ['settings', 'link_set']

def settings(request):
    from notmm.utils.django_settings import SettingsProxy
    settings = SettingsProxy(autoload=True).get_settings()
    return dict(settings=settings)

def link_set(request):
    # custom links to put on every pages
    # XXX need better configuration to allow easy maintenance
    return {'link_set': {
        'free-software' : YAMLDct('free-software.yaml')[0:8],
        'blogs-fr': YAMLDct('blogs-fr.yaml'),
        'opendata': YAMLDct('opendata.yaml'),
        'notmm-api': YAMLDct('notmm-api.yaml', randomized=False),
        #'webmaster-tools': YAMLDct('webmaster-tools.yaml'),
        'truth-alliance': YAMLDct('truth-alliance.yaml')
        #'for-sale': YAMLDct('for-sale.yaml') ## livestore links!
    }}
