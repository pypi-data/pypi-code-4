#-*- coding:utf8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'statistic.views',
    url(r'^all_time/$', 'all_time', name='statitstic_all_time'))
