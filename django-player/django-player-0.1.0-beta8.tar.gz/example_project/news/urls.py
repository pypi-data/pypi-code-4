from django.conf.urls.defaults import patterns, url

from news.views import news_list, news_detail


urlpatterns = patterns('',
    url(r'^$', news_list, name='news_index'),
    url(r'(?P<news_slug>[\w-]+)/', news_detail, name='news_detail'),
)
