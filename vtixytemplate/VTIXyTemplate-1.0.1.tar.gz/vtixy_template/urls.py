from django.conf.urls import patterns, url
from vtixy_template import views

urlpatterns = patterns('',
                       url(r'^(?P<order_id>[0-9]+)/$', views.pdf),
                       url(r'^mobile/(?P<order_id>[0-9]+)/$', views.mobile),
                       )