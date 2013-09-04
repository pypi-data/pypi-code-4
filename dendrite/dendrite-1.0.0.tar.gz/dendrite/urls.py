from django.conf.urls import patterns, url

from .views import ErrorView

urlpatterns = patterns(
    '',
    url(r'^error/$', ErrorView.as_view(), name = 'error'),
)    
