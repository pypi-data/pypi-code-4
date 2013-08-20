from django.conf.urls import patterns, url

from archer.projects import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^(?P<project_id>\d+)/path=(?P<path>\S+)$', views.show, name='show'),
                       url(r'^(?P<project_id>\d+)/$', views.show, name='show'),
                       url(r'^(?P<project_id>\d+)/upload/$', views.UploadView.as_view(), name='upload'),
                       url(r'^(?P<project_id>\d+)/deploy=(?P<path>\S+)$', views.deploy, name='deploy'),

                       url(r'^(?P<project_id>\d+)/mkdir=(?P<path>\S+)$', views.MakeDirectory.as_view(), name='mkdir'),
                       url(r'^(?P<project_id>\d+)/rmdir=(?P<path>\S+)$', views.RemoveDirectory.as_view(), name='rmdir'),
                       url(r'^(?P<project_id>\d+)/rm=(?P<path>\S+)$', views.RemoveFile.as_view(), name='rm'),
                       )
