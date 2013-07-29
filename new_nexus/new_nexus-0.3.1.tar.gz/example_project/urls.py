from django.conf.urls import patterns, include, url

from django.contrib import admin

import nexus

admin.autodiscover()
nexus.autodiscover()

urlpatterns = patterns('',
    url(r'', include(nexus.site.urls)),
)
