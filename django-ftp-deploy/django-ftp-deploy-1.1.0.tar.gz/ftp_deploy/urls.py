from django.conf.urls import patterns, include, url
from .views import DeployView

urlpatterns = patterns('',
                       url(r'^deploy/(?P<secret_key>.+)$', DeployView.as_view(), name='ftpdeploy_deploy'),
                       )
