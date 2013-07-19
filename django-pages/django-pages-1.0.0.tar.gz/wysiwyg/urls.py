from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

from django.views.generic import TemplateView

from wysiwyg.feed.feed import RssLatestPostsFeed, AtomLatestPostsFeed

urlpatterns = patterns(
    '',
    # admin part
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # ckeditor image upload connector
    url(r'^connector/browser/$', 'wysiwyg.connector.views.browser'),
    url(r'^connector/uploader/$', 'wysiwyg.connector.views.uploader'),

    # helper site (wizzard)
    url(r'^wizzard/$', TemplateView.as_view(template_name='wizzard.html')),

    # rss and atom feed
    url(r'^rss/', RssLatestPostsFeed()),
    url(r'^atom/', AtomLatestPostsFeed()),

    # robots.txt
    url(r'^robots.txt$', 'wysiwyg.views.robots'),
    # sitemap generator
    url(r'^sitemap.xml$', 'wysiwyg.views.generate_sitemap'),
    # wysiwyg url resolver
    url(r'^(?P<url>.*)$', 'wysiwyg.views.main_view'),
)
