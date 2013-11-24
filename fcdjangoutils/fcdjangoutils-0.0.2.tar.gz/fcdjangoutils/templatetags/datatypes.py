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
import math
import datetime

register = template.Library()

def nth_filter(value, param):
    try:
        if param not in value:
            return None
        return value[param]
    except:
        return getattr(value, param)

def eachnth_filter(value, param):
    return [nth_filter(part, param) for part in value]

def sum_filter(value):
    return reduce(lambda a,b: a+b, value)

def separateminus_filter(value1, value2):
    if not value1 and not value2:
        return "0"
    res = ''
    if value1:
        res += "%s" % (value1,)
    if value2:
        res += "-%s" % (value2,)
    return res

def aadd_filter(value1, value2):
    return value1 + value2

def jsonify_filter(obj):
    with Timer('jsonify'):
        return mark_safe(fcdjangoutils.jsonview.to_json(obj))

def expandforeign_filter(objs, foreign_key_col):
    with Timer('exportforeign'):
        return fcdjangoutils.jsonview.expand_foreign_key(objs, foreign_key_col)

def floor_filter(obj):
    return math.floor(obj)

@register.filter
def handle_none(obj, replacement='-'):
    if obj is None:
        return replacement
    return obj
        
@register.filter
def microseconds_to_timedelta(obj):
    if not obj: return None
    return datetime.timedelta(microseconds=float(obj))

@register.filter
def seconds_to_timedelta(obj):
    if not obj: return None
    return datetime.timedelta(seconds=float(obj))

@register.filter
def minutes_to_timedelta(obj):
    if not obj: return None
    return datetime.timedelta(minutes=float(obj))

@register.filter
def hours_to_timedelta(obj):
    if not obj: return None
    return datetime.timedelta(hours=float(obj))

@register.filter
def days_to_timedelta(obj):
    if not obj: return None
    return datetime.timedelta(days=float(obj))

@register.filter
def days_to_timedelta(obj):
    if not obj: return None
    return datetime.timedelta(days=float(obj))

@register.filter
def format_timedelta(d, fmt = "%(years)s years %(weeks)s weeks %(hours).2d:%(minutes).2d:%(seconds).2d.%(milliseconds).3d%(microseconds).3d"):
    if d is None or fmt is None:
        return None

    info = {}

    info["years"], remainder = divmod(d.days, 365)  
    info["weeks"], info["days"] = divmod(remainder, 7)   

    info["total_hours"]= (divmod(d.seconds, 3600)[0]) + d.days*24

    info["hours"], remainder = divmod(d.seconds, 3600)  
    info["minutes"], info["seconds"] = divmod(remainder, 60)   

    info["milliseconds"], info["microseconds"] = divmod(d.microseconds, 1000)  

    return fmt % info

register.filter('expandforeign', expandforeign_filter)
register.filter('jsonify', jsonify_filter)
register.filter('nth', nth_filter)
register.filter('eachnth', eachnth_filter)
register.filter('sum', sum_filter)
register.filter('separateminus', separateminus_filter)
register.filter('aadd', aadd_filter)
register.filter('floor', floor_filter)

@register.filter
def datatype(obj):
    return type(obj).__name__
