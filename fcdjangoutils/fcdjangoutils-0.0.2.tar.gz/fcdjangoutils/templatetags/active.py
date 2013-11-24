# -*- coding: utf-8 -*-

# Note, this library is free software
# Copyright 2010, 2011 FreeCode AS
# Licensed under the MIT license

from django import template
from django.core.urlresolvers import reverse
import re

register = template.Library()

@register.simple_tag
def active(request, pattern):
    if re.match(pattern, request.path):
        return "active"
    return ""

@register.simple_tag
def current_app(request):
    match = re.findall('\/([^\/]+)\/', request.path)
    if match:
        return match[0]
    return ''

