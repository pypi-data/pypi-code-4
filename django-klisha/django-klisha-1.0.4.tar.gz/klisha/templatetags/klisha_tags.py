# coding=utf-8
#
# Copyright (c) 2008-2013 by zenzire - http://www.zenzire.com
# Author Marcin Mierzejewski
#

from django import template
from klisha.models import Tag
register = template.Library()

@register.inclusion_tag('klisha/templatetags/tags_cloud.html')
def tags_cloud(font_min_size, font_max_size):
    """
    Returns tag cloud
    """
    tags = Tag.objects.all()

    entries = []
    max = 0
    for tag in tags:
        count = tag.picture_set.count()
        if count == 0:
            continue
        if count > max:
            max = count
        entries.append([count, tag])

    step = max / (font_max_size - font_min_size)
    en = []
    for count, tag in entries:
        try:
            en.append([count/step+font_min_size, tag])
        except:
            en.append([font_min_size, tag])
        
    return { 'tags': en }