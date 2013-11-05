from django.conf.urls.defaults import patterns, url
from django.views.generic import DetailView

from .models import OnCall


urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w\d]+)/$',
        DetailView.as_view(model=OnCall),
        name='on-call'),
    )
