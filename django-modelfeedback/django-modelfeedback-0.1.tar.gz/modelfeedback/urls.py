from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _
from modelfeedback.views import (FeedbackCreateView,
                                 FeedbackDetailView)


urlpatterns = patterns(
    '',

    url(_(r'^create/(?P<app_label>[_\w]+)/(?P<model>[_\w]+)'
          '/(?P<object_id>[0-9]+)$'), FeedbackCreateView.as_view(),
        name='create'),
    url(_(r'^detail/(?P<pk>[0-9]+)$'),
        FeedbackDetailView.as_view(), name='detail'),
)
