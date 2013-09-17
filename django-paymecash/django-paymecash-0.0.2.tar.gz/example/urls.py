# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import PayPageView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', PayPageView.as_view(), name='pay_page'),
    url(r'^paymecash/', include('paymecash.urls')),
    url(r'^admin/', include(admin.site.urls)),
)