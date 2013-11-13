from django.conf.urls.defaults import patterns, url
from django.views.generic import DetailView, ListView

from .models import OnCall


urlpatterns = patterns('',
    url(r'^$',
        ListView.as_view(model=OnCall),
        name='on-calls'),
    url(r'^(?P<slug>[-\w\d]+)/$',
        DetailView.as_view(model=OnCall),
        name='on-call'),
    )
