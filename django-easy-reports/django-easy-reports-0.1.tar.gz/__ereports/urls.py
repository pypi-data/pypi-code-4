# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url
from pasportng.pasport.urls2 import secure_url
from .views import ReportIndex, PayrollView, ReportView, ReportConfigView


urlpatterns = patterns(
    '',

    secure_url(r'^(?P<office>[\w\d]+)/$',
               ReportIndex.as_view(),
               name='ereports.list_office_reports'),

    secure_url(r'^(?P<office>[\w\d]+)/(?P<year>\d+)/(?P<month>\w+)/(?P<format>\w+)/$',
               PayrollView.as_view(),
               name="ereports.payroll_of"),

    secure_url(r'^(?P<office>[\w\d]+)/report/(?P<report>\d+)/configure/$',
               ReportConfigView.as_view(),
               name='ereports.configure'),

    secure_url(r'^(?P<office>[\w\d]+)/(?P<report>\d+)/(?P<format>\w+)/$',
               ReportView.as_view(),
               name='ereports.do_report'),

    secure_url(r'^(?P<office>[\w\d]+)/(?P<report>\d+)/(?P<format>(html|csv|xls))/$',
               ReportView.as_view(),
               name='ereports.do_report'),

    secure_url(r'^(?P<office>[\w\d]+)/(?P<report>\d+)/$',
               ReportView.as_view(), name='ereports.do_report',
               kwargs={'format': 'html'}),

    url(r'^model/info/(?P<owner>.+)/(?P<app_name>\w+)/(?P<model_name>\w+)/$', 'pasportng.ereports.views.get_model_meta',
        name='get_model_meta'),

)
