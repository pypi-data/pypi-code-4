from django.conf.urls import patterns, include, url
from rsbp.views import PostListView, PostView, TagView
from rsbp.feeds import LatestPostsFeed

urlpatterns = patterns('',
    url(r'^$', PostListView.as_view(), name='index'),
    url(r'^page/(?P<page>\d+)/$', PostListView.as_view(), name='page'),
    url(r'^(?P<post_id>\d+)(?:\/(?P<title_slug>[^/]+))?/$', PostView.as_view(), name='post'),
    url(r'^tagged/(?P<tags>[-/\w\.\ ]+)/$', TagView.as_view(), name='tags'),
    url(r'^rss/$', LatestPostsFeed(), name='feed'),
)
