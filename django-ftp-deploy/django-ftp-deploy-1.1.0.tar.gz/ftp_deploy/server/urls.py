from django.conf.urls import patterns, include, url
from .views import DashboardView, LogView, LogSkipDeployView, BitbucketAPIView
from .views import ServiceManageView, ServiceRestoreView, ServiceEditView, ServiceAddView, ServiceStatusView, ServiceDeleteView

urlpatterns = patterns('',
                       url(r'^dashboard/$', DashboardView.as_view(), name='ftpdeploy_dashboard'),
                       url(r'^log/$', LogView.as_view(), name='ftpdeploy_log'),
                       url(r'^log/(?P<pk>\d+)/skip/$', LogSkipDeployView.as_view(), name='ftpdeploy_log_skip'),

                       url(r'^service/add$', ServiceAddView.as_view(), name='ftpdeploy_service_add'),
                       url(r'^service/(?P<pk>\d+)/manage$', ServiceManageView.as_view(), name='ftpdeploy_service_manage'),
                       url(r'^service/(?P<pk>\d+)/edit$', ServiceEditView.as_view(), name='ftpdeploy_service_edit'),
                       url(r'^service/(?P<pk>\d+)/delete$', ServiceDeleteView.as_view(), name='ftpdeploy_service_delete'),
                       url(r'^service/(?P<pk>\d+)/status/$', ServiceStatusView.as_view(), name='ftpdeploy_service_status'),
                       url(r'^service/(?P<pk>\d+)/restore/$', ServiceRestoreView.as_view(), name='ftpdeploy_service_restore'),
                       url(r'^service/(?P<pk>\d+)/bbapi/$', BitbucketAPIView.as_view(), name='ftpdeploy_bb_api'),
                       )
