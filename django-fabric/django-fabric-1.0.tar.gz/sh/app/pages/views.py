# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from sh.app.pages.forms import PageForm
from sh.app.pages.models import Category, Page

def view_category(request, category_slug='default'):

    category = get_object_or_404(Category,slug=category_slug)
    category_navigation = Page.objects.filter(is_active=True, category=category)

    return render(request, "pages/category.html", {
        'category': category,
        'category_navigation': category_navigation,
    })


def view_page(request, category_slug=None, page_slug=None):
    if page_slug is None:
        page = cache.get('frontpage')
        if page is None:
            page = Page.objects.get(pk=settings.FRONTPAGE_ID)
            cache.set('frontpage', page)

    else:
        key = 'page%s' % page_slug
        page = cache.get(key)
        if page is None:
            page = get_object_or_404(Page, is_active=True, slug=page_slug)
            cache.set(key, page)


    return render(request, "pages/view_page.html", {
        'page': page,
        })

@login_required
def edit_page(request, id=None):

    if id is None:
        page = Page()
    else:
        page = get_object_or_404(Page, pk=id)

    form = PageForm(instance=page)

    if request.method == 'POST':
        form = PageForm(request.POST, instance=page)
        if form.is_valid():
            page = form.save()
            messages.success(request, _('Page successfully saved'))
            return redirect(reverse('view_page', args=[page.slug]))

    return render(request, 'pages/edit_page.html', {
        'page': page,
        'form': form
    })

@login_required
def delete_page(request, id):

    if int(id) == settings.FRONTPAGE_ID:
        messages.error(request, _('This page is the front page and cannot be deleted'))
        return redirect(reverse('edit_page', args=[id]))

    page = get_object_or_404(Page, pk=id)
    if request.method == 'POST':
        if request.POST.get('delete') == 'true':

            page.delete()
            messages.success(request, _('The page was deleted'))
            return redirect(reverse('view_dashboard'))

    return render(request, 'pages/delete_page.html', {
        'page': page,
    })
