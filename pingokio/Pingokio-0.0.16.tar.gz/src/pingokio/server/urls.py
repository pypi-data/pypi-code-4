from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', RedirectView.as_view(url='/statistic/all_time/'), name='redirecto-all-time-statistic'),
    url(r'^statistic/', include('pingokio.statistic.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
