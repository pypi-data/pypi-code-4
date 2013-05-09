from django.conf.urls.defaults import *
from surlex.dj import surl

import views

urlpatterns = patterns('',
    surl(r'^<country>/<year:Y>(-<other_year:Y>)/(<province>/)$', views.holidays, name="public_holidays"),
)