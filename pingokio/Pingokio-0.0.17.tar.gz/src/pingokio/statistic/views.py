#-*- coding:utf-8 -*-
from django.shortcuts import render

from pingokio.domains.models import Domain


def all_time(request):
    return render(request, 'statistic/all_time.html', {'domains': Domain.objects.all()})
