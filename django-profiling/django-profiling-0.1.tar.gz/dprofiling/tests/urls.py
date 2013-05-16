from django.conf.urls import patterns, url
from django.views.generic import RedirectView

from dprofiling.tests import views



urlpatterns = patterns('',
    url(r'^a/$', views.HelloWorld.as_view()),
    url(r'^b/$', views.HelloWorld.as_view()),
    url(r'^c/$', views.HelloWorld.as_view()),
    url(r'^d/$', views.ExceptionView.as_view()),
    url(r'^e/$', views.NotFoundView.as_view()),
    url(r'^f/$', RedirectView.as_view(url='/a/')),
)
