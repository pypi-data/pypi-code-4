"""URLs to run the tests."""
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^faq/', include('frequently.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('cms.urls')),
)

urlpatterns += staticfiles_urlpatterns()
