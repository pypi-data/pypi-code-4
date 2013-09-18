from django.conf.urls import patterns, url, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$','pml.test_view.home', name='home'),
    url(r'^redirect/$','pml.test_view.go_back', name='go_back'),
    url(r'^admin/', include(admin.site.urls)),
)
