#!/usr/bin/python
# -*- coding: utf-8 -*-

import grok


class AddUsers(grok.Permission):
    grok.name('dolmen.security.AddUsers')
    grok.title('dolmen.security: add users')


class ManageUsers(grok.Permission):
    grok.name('dolmen.security.ManageUsers')
    grok.title('dolmen.security: manage users')
