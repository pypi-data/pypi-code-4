from django.conf.urls import patterns, url

from switter.views import SwitterTweetsView

urlpatterns = patterns('',
    url(r'^(?P<query_type>[_\w]+)/$', SwitterTweetsView.as_view(), name="switter_tweets"),
)
