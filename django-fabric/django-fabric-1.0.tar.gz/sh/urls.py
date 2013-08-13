
from django.conf import settings
from django.conf.urls import patterns, url, include

from django.contrib import admin
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

admin.autodiscover()

import os

urlpatterns = patterns('',
    url(r'^google40fdd297a3739dce.html$', lambda r:HttpResponse("google-site-verification: google40fdd297a3739dce.html")),
    url(r'^admin/django/',  include(admin.site.urls), name='django_admin'),

    url(r'dashboard/', include('sh.app.dashboard.urls')),
    url(_(r'news/'), include('sh.app.news.urls')),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^accounts/logout/$', 'sh.app.dashboard.views.logout', name='logout'),
    url(r'^fkjfbfeionafkdnfabkjf/$','sh.core.views.backup_auto'),
    url(r'^ckeditor/', include('ckeditor.urls')),

    url(r'', include('sh.app.pages.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^uploads/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': os.path.join(settings.ROOTPATH, 'files/static')}),
    )
