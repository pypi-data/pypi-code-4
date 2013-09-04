from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView

from django.contrib import admin
admin.autodiscover()

from polls.views import ResultsView, PollView, PollVoteView, PollListView
from polls.forms import PollForm, PollVoteForm
from polls.models import Poll

urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)$', login_required(PollView.as_view()), name='poll_edit'),
    url(r'^submit/$', login_required(PollView.as_view()), name='poll_add'),
    url(r'^vote/(?P<pk>\d+)$', login_required(PollVoteView.as_view()), name='poll_vote'),
    url(r'^results/(?P<pk>\d+)$', ResultsView.as_view(), name='poll_results'),
    url(r'^$', ListView.as_view(queryset=Poll.objects.order_by('-created'), template_name='polls/index.html'), name='polls'),
    url(r'^polls/$', PollListView.as_view(), name='polls_user'),
    url(r'^admin/', include(admin.site.urls)),
)
