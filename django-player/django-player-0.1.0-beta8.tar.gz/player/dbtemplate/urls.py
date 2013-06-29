from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('player.dbtemplate.views',
    url(r'^$', 'template_list', name='template_list'),
    url(r'^add/$', 'template_add', name='template_add'),
    url(r'^(?P<template_id>\d+)/$', 'template_detail', name='template_detail'),
    url(r'^(?P<template_id>\d+)/edit/$', 'template_edit', name='template_edit'),
)
