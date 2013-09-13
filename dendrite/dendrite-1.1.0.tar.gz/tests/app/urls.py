from django.conf.urls import url, patterns

from .views import * 

urlpatterns = patterns(
    '',
    url('^$', TwitterConnectView.as_view()),
    url('^social/twitter/callback/$', TwitterCallbackView.as_view()),
)
