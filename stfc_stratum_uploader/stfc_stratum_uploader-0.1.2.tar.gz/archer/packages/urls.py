from django.conf.urls import patterns, url

from archer.packages import views

urlpatterns = patterns('',
                       url(r'^(?P<package_id>\d+)/$', views.show, name='show'),
                       url(r'^(?P<package_id>\d+)/deploy/$', views.deploy, name='deploy'),
                       url(r'^(?P<package_id>\d+)/remove/$', views.remove, name='remove'),
)