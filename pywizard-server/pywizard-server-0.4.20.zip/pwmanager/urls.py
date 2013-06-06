from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.contrib.sites.models import Site
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from pwmanager.nodes.views import node_viewer, home, package_upload

admin.autodiscover()
# admin.site.unregister(Site)

urlpatterns = patterns('',
   # Examples:
   # url(r'^$', 'pwmanager.views.home', name='home'),
   # url(r'^pwmanager/', include('pwmanager.foo.urls')),

   # Uncomment the admin/doc line below to enable admin documentation:
   # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),


   url(r'^$', home),
   url(r'^node/(?P<name>.+)', node_viewer),

   url(r'^api/package/(?P<group>.+)', package_upload),

   # Uncomment the next line to enable the admin:
   url(r'^admin/', include(admin.site.urls)),
   # (r'^grappelli/', include('grappelli.urls')),
)


urlpatterns += staticfiles_urlpatterns()