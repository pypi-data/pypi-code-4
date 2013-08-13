# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from sh.app.news.models import NewsItem
from sh.app.pages.models import Page
from django.contrib.auth import logout as auth_logout

@login_required
def view_dashboard(request):

    pages = Page.objects.all()
    news = NewsItem.objects.all()

    return render(request, 'dashboard/base.html', {
        'pages': pages,
        'news': news,
    })

def logout(request):
    auth_logout(request)
    return redirect(reverse('view_page'))