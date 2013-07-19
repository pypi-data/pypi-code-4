from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    url(r'^users/$', views.Index.as_view(), name='djangopypi2-users'),
    url(r'^users/(?P<username>[\w-]+)/$', views.UserDetails.as_view(), name='djangopypi2-user-profile'),
)
