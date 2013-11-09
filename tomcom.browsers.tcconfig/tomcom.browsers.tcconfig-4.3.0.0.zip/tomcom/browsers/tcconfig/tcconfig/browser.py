#!/usr/bin/python
# -*- coding: utf-8 -*-

from tomcom.browser.public import *
from BTrees.OOBTree import OOBTree

class ITCConfig(Interface):

    def set(self):
        """ """

    def get(self,key,default=None):
        """ """

class Browser(BrowserView):

    implements(ITCConfig)

    def _set(self,key,value):

        context=self.context
        annotation=context.getAdapter('annotation')

        if not annotation.has_key(key):
            annotation[key]=OOBTree()
        annotation[key].update(value)

    def set(self):
        """ """
        context=self.context

        context.getBrowser('tpcheck').auth_tcconfig_manage()

        form=context.REQUEST.form
        key=form.get('key')
        self._set(key,form)

        message=context.getAdapter('message')
        message('Changes saved.')
        return context.REQUEST.RESPONSE.redirect(context.REQUEST['HTTP_REFERER'])

    def get(self,key,default=None):

        context=self.context
        annotation=context.getAdapter('annotation')
        return annotation.get(key,default)
