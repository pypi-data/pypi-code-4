from django.template import Library
from djinn_announcements.settings import STATUS_CLASSES


register = Library()


@register.filter
def statusclass(status):

    return STATUS_CLASSES.get(status, "")
