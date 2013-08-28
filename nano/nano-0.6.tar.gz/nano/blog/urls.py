from copy import deepcopy
import datetime

from django.conf.urls.defaults import *

from nano.blog.models import *

news_dict = {
        'queryset': Entry.objects.all().order_by('-pub_date'),
        'extra_context': {
                'me': 'news',
                'now_today': datetime.date.today(),
                },
}

news_date_dict = deepcopy(news_dict)
news_date_dict['date_field'] = 'pub_date'

news_date_latest = deepcopy(news_date_dict)
news_date_latest['template_object_name'] = 'object_list'

news_date_year = deepcopy(news_date_dict)
news_date_year['make_object_list'] = True
news_date_year['allow_empty'] = True

news_date_month = deepcopy(news_date_dict)
news_date_month['month_format'] = '%m' 
news_date_month['allow_empty'] = True

urlpatterns = patterns('django.views.generic',
        (r'^(?P<year>\d{4})/(?P<month>[01]\d)/(?P<day>[0123]\d)/$', 'date_based.archive_day', news_date_month),
        (r'^(?P<year>\d{4})/(?P<month>[01]\d)/$', 'date_based.archive_month', news_date_month),
        (r'^(?P<year>\d{4})/$', 'date_based.archive_year', news_date_year),
        (r'^latest/$',              'date_based.archive_index', news_date_latest),
        (r'^today/$',               'date_based.archive_today', news_date_month),
        (r'^$',                     'list_detail.object_list', news_dict),
        #(r'^language/p(?P<page>[0-9]+)/$',          'list_detail.object_list', dict(language_list_dict)),

        #(r'^value/(?P<object_id>[0-9]+)/$',         'list_detail.object_detail', dict(value_detail_dict)),
)
