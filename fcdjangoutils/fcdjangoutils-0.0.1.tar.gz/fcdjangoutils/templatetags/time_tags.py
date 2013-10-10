# Note, this library is free software
# Copyright 2010 FreeCode AS
# Licensed under the MIT license

from django import template
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.utils import simplejson
import django.db.models.base
import fcdjangoutils.jsonview
from django.utils.safestring import mark_safe
from fcdjangoutils.timer import Timer
from django.utils.translation import ugettext_lazy as _
import warnings

import math

register = template.Library()

@register.filter
def duration(duration):
    warnings.warn("Use templatetags from {% load datatypes %} instead", DeprecationWarning)
    if duration is None:
        return '-'
    return '%d:%02d' % (duration/60, duration%60)


@register.filter
def duration_verbose(duration):
    warnings.warn("Use templatetags from {% load datatypes %} instead", DeprecationWarning)
    if duration is None:
        return '-'
    hours = int(math.floor(duration/3600));
    minutes = int(math.floor((duration%3600)/60));
    seconds = int(math.floor(duration%60));

    res = ""
    first = True
    if hours != 0:
        res += _("%d hours") % hours;
        first = False

    if minutes != 0:
        if not first: res += ", "
        res += _("%d min") % minutes;
        first = False

    if seconds != 0:
        if not first: res += ", "
        res += _("%d sec") % seconds;

    #return '%d:%02d' % (duration/60, duration%60)
    return res

@register.filter
def duration_diff(dd):
    if dd is None:
        return '-'
    if dd == 0:
        return _("No change")
    if dd > 0:
        suffix = _("better")
    else:
        suffix  = _('worse')

    dd = abs(dd)
    res = ""
    if dd > 60:
        res += _("%d minutes") % (dd/60)
        res += " "
    res += _("%d seconds") % (dd%60)

    res += " "
    res += suffix.encode("utf-8")
    return res
