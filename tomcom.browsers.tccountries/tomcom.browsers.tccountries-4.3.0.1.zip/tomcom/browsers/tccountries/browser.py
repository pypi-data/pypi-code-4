#!/usr/bin/python
# -*- coding: utf-8 -*-

from tomcom.browsers.base import *

class ITCCountries(Interface):

    def get_as_list(self):
        """ """

    def get_country_for_code(self,string_):
        """ """


class Browser(BrowserView):

    implements(ITCCountries)

    def get_as_list(self):

        context=self.context
        pl=context.getAdapter('pl')()
        langcode=context.getAdapter('langcode')()
        translate=context.getAdapter('translate')

        list_=[]

        for code,name in pl.listAvailableCountries():
            code=str(code)
            name=translate(msgid=code,
                           domain='plone',
                           default=name,
                           target_language=langcode)

            list_.append((code,name,))
        list_.sort(lambda a,b:cmp(a[1],b[1]))

        return list_


    def get_country_for_code(self,string_):

        for code,country in self.get_as_list():
            if string_==code:
                return country

        return ''