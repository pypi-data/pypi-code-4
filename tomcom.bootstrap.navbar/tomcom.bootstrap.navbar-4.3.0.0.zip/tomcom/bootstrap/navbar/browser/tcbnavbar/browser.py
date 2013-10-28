#!/usr/bin/python
# -*- coding: utf-8 -*-

from tomcom.browser.public import *
from Products.CMFCore.Expression import Expression,getExprContext
from Products.CMFCore.interfaces._tools import IActionCategory, IAction

class ITCBNavBar(Interface):

    def get(self):
        """ """

class Browser(BrowserView):

    implements(ITCBNavBar)

    def get(self,categories,hidden=True):

        context=self.context
        pa=context.getAdapter('pa')()
        checkPerm=context.getAdapter('checkperm')
        translate=context.getAdapter('translate')

        self._list=[]
        for category in categories:
            #Could be category or action
            category_dict=self._set_item(pa[category],self._list)
            for item in pa[category].objectValues():
                current_dict=self._set_item(item,category_dict['children'])
                if IActionCategory.providedBy(item):
                    self._recurse(item,current_dict['children'])

        return self._list

    def _set_item(self,item,current):
        """ """
        context=self.context
        check_perm=context.getAdapter('checkperm')
        translate=context.getAdapter('translate')

        if IAction.providedBy(item):
            for permission in item.permissions:
                if not check_perm(permission):
                    return

        dict_={}

        if IAction.providedBy(item):
            dict_['title']=translate(msgid=getattr(item,'msgid',item.title),domain=item.i18n_domain,default=item.title)
        else:
            dict_['title']=item.title

        if IActionCategory.providedBy(item):
            dict_['children']=[]
            dict_['interface']='IActionCategory'

        if IAction.providedBy(item):
            dict_['interface']='IAction'
            dict_['target']=item.getProperty('link_target','_self')
            dict_['class']=item.getProperty('class_','')
            dict_['url']=Expression(item.url_expr)(getExprContext(context,context))

        current.append(dict_)

        return dict_

    def _recurse(self,current_item,list_children):
        """ """
        for item in current_item.objectValues():
            current_dict=self._set_item(item,list_children)
            if IActionCategory.providedBy(item):
                self._recurse(item,current_dict['children'])
