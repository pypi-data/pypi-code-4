# -*- coding: utf-8 -*-
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.views.generic.list_detail import object_list

from Sveetchies.django.news import NEWS_ENTRIES_PAGINATION
from Sveetchies.django.news.models import Category, Entry

def category_details_by_slug(request, category_slug):
    """
    Catégorie détails et liste des billets
    """
    template = 'news/category_details.html'

    category_object = get_object_or_404(Category, visible=True, slug=category_slug)
    
    entries_queryset = category_object.entry_set.publishable_filter().order_by('-publish_date')
    
    extra_context = {
        'category_object': category_object,
    }
    
    response = object_list(
        request,
        queryset=entries_queryset,
        paginate_by=NEWS_ENTRIES_PAGINATION,
        template_name=template,
        extra_context=extra_context,
        allow_empty=True
    )
    return response

def entry_details_by_slug(request, category_slug, entry_slug):
    """
    Billet détails
    """
    template = 'news/entry_details.html'

    entry_object = Entry.objects.get_publishable_or_404(category__slug=category_slug, slug=entry_slug)
    
    extra_context = {
        'category_object': entry_object.category,
        'entry_object': entry_object,
    }
    
    return render_to_response(template, extra_context, context_instance=RequestContext(request))
