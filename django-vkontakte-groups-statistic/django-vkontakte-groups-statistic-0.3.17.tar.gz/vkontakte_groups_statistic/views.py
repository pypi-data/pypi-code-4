# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response
from models import VkontakteDeniedAccessError, Group, parse_statistic_for_group
from forms import GroupImportStatisticForm
import re
import logging

log = logging.getLogger('vkontakte_groups_statistic')

# TODO: move these views to vkontakte_groups_statistic app
def import_statistic(request, redirect_url_name=None, form_class=GroupImportStatisticForm):

    context = {
        'message': '',
    }

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            try:
                group = form.save()
                if redirect_url_name:
                    try:
                        return HttpResponseRedirect(reverse(redirect_url_name, args=('vk', group.id)))
                    except:
                        context['message'] = u'Статистика группы импортирована успешно'
            except VkontakteDeniedAccessError:
                context['message'] = u'Вы не имеете доступа к статистике группы'
    else:
        form = form_class()

    context['form'] = form

    return render_to_response('vkontakte_groups_statistic/import_group_statistic.html', context, context_instance=RequestContext(request))

@csrf_exempt
def import_statistic_via_bookmarklet(request, redirect_url_name=None, redirect_kwargs=None):
    # TODO: show errors instead of redirect
    try:
        url, content = request.POST['url'], request.POST['body']
    except KeyError:
        return HttpResponseRedirect('/')

    # http://vk.com/stats?act=activity&gid=29607900
    # http://vk.com/stats?gid=29607900
    m = re.findall(r'http://vk.com/stats\?(?:act=([^&]+)&)?gid=(\d+)/?', url)
    if len(m) == 0:
        log.error("Url of vkontakte group statistic should be started with http://vk.com/stats?gid=")
        return HttpResponseRedirect('/')

    act, group_id = m[0]
    group = Group.remote.fetch(ids=[group_id])[0]

    parse_statistic_for_group(group, act, content)

    if redirect_kwargs is None:
        redirect_kwargs = {}
    redirect_kwargs['object_id'] = group.id

    try:
        return HttpResponseRedirect(reverse(redirect_url_name, kwargs=redirect_kwargs))
    except:
        return HttpResponseRedirect('/')