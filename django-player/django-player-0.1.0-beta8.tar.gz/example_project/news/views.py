from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from news.models import NewsItem


def news_list(request):
    all_news = NewsItem.objects.all()
    return render_to_response('news/news_list.html',
                              {'news_list': all_news},
                              context_instance=RequestContext(request))


def news_detail(request, news_slug):
    news_item = get_object_or_404(NewsItem, slug=news_slug)
    return render_to_response('news/news_detail.html',
                              {'news_item': news_item},
                              context_instance=RequestContext(request))


def views_to_register():
    """ returns views to be registered with dbresolver """
    return (
        (news_list, _('News listing')),
        (news_detail, _('News item detail')),
    )
