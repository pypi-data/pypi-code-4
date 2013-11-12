from django.conf.urls import patterns, include, url
from django.shortcuts import redirect
from django.contrib import admin

admin.autodiscover()


def home(request):
    return redirect('/admin/')


urlpatterns = patterns(
    '',
    url(r'^$', home, name='home'),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
