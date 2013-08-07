# encoding: utf-8
"""
Some views for the django weblog app.

"""
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from weblog.models import Category, Post


def archive_index(request):
    """Create a list with (year, months) tuples and render them."""
    archive = [
        (date.year, Post.published.filter(pub_date__year=date.year).dates(
                'pub_date', 'month', order='DESC'))
        for date in Post.published.dates('pub_date', 'year', order='DESC')]

    return render_to_response('weblog/post_archive.html',
            {'archive': archive},
            context_instance=RequestContext(request))


def category_detail(request, path):
    """Show the category specified by ``pyth``."""
    category = get_object_or_404(Category, path__iexact=path)
    return render_to_response('weblog/category_detail.html',
            {'category': category},
            context_instance=RequestContext(request))
