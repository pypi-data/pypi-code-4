#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
from django.conf.urls import patterns, url
from .views import Login, SignUp, Logout, Profile, ForgotPassword  #  Manage, ListUsers

urlpatterns = patterns('',
    url(r'^login/?', Login.as_view(), name='users.login'),
    url(r'^logout/?', Logout.as_view(), name='users.logout'),
    url(r'^profile/?', Profile.as_view(), name='users.profile'),
    url(r'^signup/?', SignUp.as_view(), name='users.signup'),
    url(r'^forgot_password/?', ForgotPassword.as_view(), name='users.forgot_password'),

    #url(r'^/?', ListUsers.as_view(), name='users.list_all'),
    #url(r'^manage/?', Manage.as_view(), name='users.manage'),
    #url(r'^create/?', Manage.as_view(), name='users.manage'),
    #url(r'^edit/(\d)/?', Manage.as_view(method='edit_users'), name='users.manage'),
)
