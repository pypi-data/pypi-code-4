# -*- coding: utf-8 -*-
import re
import urllib2
import datetime
from django.core.urlresolvers import reverse
from django.template.base import Library
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
from sh.app.feed.util import IMAGE_FILE_TYPES
from sorl.thumbnail.shortcuts import get_thumbnail


register = Library()

url_re = '((http):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)'

@register.filter
def boolean(value, arg=None):
    if value: return mark_safe('<img src="/static/icons/accept.png" style="max-width:28px;" alt="%s" />' % _('Yes'))
    elif value is None: return mark_safe('<img src="/static/icons/question.png" style="max-width:28px;" alt="%s" />' % '?')
    return mark_safe('<img src="/static/icons/delete.png" style="max-width:28px;" alt="%s"/>' % _('No'))

@register.filter
def time_since(value, arg=None):
    now = datetime.datetime.now()
    diff = now - value
    if diff.seconds < 60:
        return unicode(_('Just now'))
    return _('%s ago') % timesince(value)

def get_title_for_link(link):
    file_type = link.split(".")[len(link.split("."))-1]
    if file_type in IMAGE_FILE_TYPES:
        im = get_thumbnail(link, '100x100', crop='center', quality=99)
        return mark_safe('<img src="%s" alt="" />' % im.url)
    try:
        page = urllib2.urlopen(urllib2.Request(link)).read()
        return re.search('<title>.*</title>', page).group().replace('<title>','').replace('</title>','')
    except:
        return link



def url_text(link):
    key = re.sub('^(http|https)\://', '', link)
    key = key.replace(".","").replace("-","").replace("_","").replace("/","")
    text = cache.get(key)
    title = get_title_for_link(link)
    if not text:
        new_link = mark_safe('<a href="%s">%s</a>' % (link, title))
        cache.set(key, new_link)
        return mark_safe(new_link)
    return mark_safe(text)



@register.filter
def links(value, arg=None):
    value = unicode(value)
    url = re.search(url_re, value)
    if url:
        value = re.sub(url_re, url_text(url.group()), value)
    return mark_safe(value)

    


@register.filter
def user_mentions(value, arg=None):
    value = unicode(value)
    name = re.search('@[a-z]+', value)
    if name:
        value = re.sub('@[a-z]+', get_profile_link(name.group()), value)
    return mark_safe(value)

def get_profile_link(name):
    from django.contrib.auth.models import User
    try:
        name = name.replace("@", "")
        u = User.objects.get(username=name)
        return '<a href="%s">%s</a>' % (reverse('view_profile', args=[u.pk]), u.get_full_name())
    except (TypeError, User.DoesNotExist):
        return name