# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from sh.app.news.forms import NewsItemForm
from sh.app.news.models import NewsItem

def news_feed(request):

    page = request.GET.get('page')

    news = cache.get('news')

    if news is None:
        news = NewsItem.objects.filter(pub_date__lte=datetime.now())

    paginator = Paginator(news, 10) # Show 25 contacts per page

    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        news = paginator.page(paginator.num_pages)

    return render(request, 'news/feed.html', {
        'news': news,
    })

def view_item(request, item_slug):
    key = 'item%s' % item_slug
    item = cache.get(key)
    if item is None:
        item = get_object_or_404(NewsItem, is_active=True, slug=item_slug)
        cache.set(key, item)

    return render(request, "news/view_item.html", {
        'item': item,
        })

@login_required
def edit_item(request, id=None):

    if id is None:
        item = NewsItem()
    else:
        item = get_object_or_404(NewsItem, pk=id)

    form = NewsItemForm(instance=item)

    if request.method == 'POST':
        form = NewsItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            messages.success(request, _('News item successfully saved'))
            return redirect(reverse('view_item', args=[item.slug]))

    return render(request, 'news/edit_item.html', {
        'item': item,
        'form': form
    })
