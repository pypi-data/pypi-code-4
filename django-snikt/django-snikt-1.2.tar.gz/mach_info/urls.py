from django.conf.urls import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from mach_info import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^sent/(?P<num>\d+)/$', views.sent, name='sent'),
    url(r'^allstatus/$',views.allstatus,name='allstatus'),
    url(r'^delete/(?P<num>\d+)/(?P<svc_tag>.+)/$',views.delete, name='delete'),
    url(r'^demo_status/(?P<svc_tag>.+)/$',views.demo_status, name='demo_status'),
)
urlpatterns += staticfiles_urlpatterns()