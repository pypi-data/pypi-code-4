# -*- coding: utf-8 -*-
"""
Url's map "racine"
"""
from django.conf.urls.defaults import *

from Sveetchies.django.tribune.views.remote import *

urlpatterns = patterns('',
    #url(r'^$', PageIndex.as_view(), name='documents-index'),
    
    url(r'^remote/$', MessagePlainView.as_view(), name='remote-plain'),
    url(r'^remote/json/$', MessageJsonView.as_view(), name='remote-json'),
    url(r'^remote/xml/$', MessageXmlView.as_view(), name='remote-xml'),
)
