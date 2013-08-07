# encoding: utf-8
from django.conf.urls.defaults import patterns, url
from django.views.generic import date_based, list_detail
from haystack.forms import SearchForm
from haystack.query import SearchQuerySet
from haystack.views import SearchView

from weblog.models import Category, Post


# Used for the weblog index and pages (page/i)
post_index_info = {
    'queryset': Post.published.all(),
    'paginate_by': 10,
    'template_object_name': 'post',
}

# Used for the year archive
post_archive_year_info = {
    'queryset': Post.published.all(),
    'date_field': 'pub_date',
    'template_object_name': 'post',
}

# Used for month archive, day archive and post detail
post_archive_info = dict(post_archive_year_info, month_format='%m')

# Used for category listing
category_info = {
    'queryset': Category.objects.filter(parent=None),
    'template_object_name': 'category',
}

sqs = SearchQuerySet().models(Post)


urlpatterns = patterns('weblog.views',
    url(r'^$',
            list_detail.object_list,
            dict(post_index_info, page='1'),
            name='weblog_index'),
    url(r'^page/(?P<page>\d+)/$',
            list_detail.object_list,
            post_index_info,
            name='weblog_page'),

    url(r'^archive/$',
            'archive_index',
            name='archive_index'),
    url(r'^(?P<year>\d{4})/$',
            date_based.archive_year,
            post_archive_year_info,
            name='weblog_archive_year'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
            date_based.archive_month,
            post_archive_info,
            name='weblog_archive_month'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
            date_based.archive_day,
            post_archive_info,
            name='weblog_archive_day'),

    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)/$',
            date_based.object_detail,
            dict(post_archive_info, slug_field='slug',
                extra_context={'single_post': True}),
            name='weblog_post_detail'),

    url(r'^category/$',
            list_detail.object_list,
            category_info,
            name='weblog_category_list'),
    url(r'^category/(?P<path>(([\w-]+)/)+)$',
            'category_detail',
            name='weblog_category_detail'),

    url(r'^search/', SearchView(
            template='weblog/search.html',
            searchqueryset=sqs,
            form_class=SearchForm,
        ), name='haystack_search'),
)
