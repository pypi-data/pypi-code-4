#!/usr/bin/env python
# -*- coding: utf-8 -*-

from notmm.utils.urlmap import RegexURLMap, url

# XXX todo and profit :)
# urlmap = RegexURLMap(backend=MySQLBackend)
# urls = urlmap.connect() # obtain cursor for adding/removing new routes
# urlpatterns = urls.publish() # publish SELECTed routes into the current module
urlpatterns = RegexURLMap()

urlpatterns.add_routes('blogengine.contrib.userprofile.list_views',
    #User profile page (dashboard with personalized content)
    #url(r'(?P<username>[\w]+)/', 'dashboard'),
    #User list
    url(r'^users/$', 'users'),
)

