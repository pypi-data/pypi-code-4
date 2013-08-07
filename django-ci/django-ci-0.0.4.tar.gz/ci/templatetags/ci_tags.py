from django.template.base import Library
import datetime
from django.template.defaultfilters import date


register = Library()

@register.filter
def host_only(request):
    return request.get_host().rsplit(":", 1)[0]


@register.filter
def timestamp(commit_time, format=None):
    date = datetime.datetime.fromtimestamp(commit_time)
    if format:
        return date(date, format)
    return date
