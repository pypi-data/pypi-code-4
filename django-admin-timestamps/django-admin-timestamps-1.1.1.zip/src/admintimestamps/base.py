import datetime
from django.template.defaultfilters import date
from django.contrib.humanize.templatetags.humanize import naturalday

try:
    from django.contrib.humanize.templatetags.humanize import naturaltime
except ImportError:
    from .compat.humanize import naturaltime

DEFAULT_TIMESTAMP_FIELDS = ('created', 'modified')


def human_timestamp(value):
    """
    Converts the given date(time) value to a more readable string.

    If the delta between now and the given value is < 1 day it
    will return strings like 'a second ago', '2 hours ago' etc.

    Otherwise the datetime will be formatted according to the given
    format or ``SHORT_DATE(TIME)_FORMAT``
    """
    if not value:
        return ''
    today = datetime.date.today()
    if isinstance(value, datetime.datetime):
        delta = today - value.date()
        fmt = 'SHORT_DATETIME_FORMAT'
        display_method = naturaltime
        delta_range = [0]
    else:
        delta = today - value
        fmt = 'SHORT_DATE_FORMAT'
        display_method = naturalday
        delta_range = [-1, 0, 1]
    if delta.days in delta_range:
        return display_method(value)
    return date(value, fmt)


class TimestampedChangelist(object):
    """
    Custom changelist implementation that adds human readable
    timestamp fields to the list display.
    """

    def __init__(self, *args, **kwargs):
        super(TimestampedChangelist, self).__init__(*args, **kwargs)
        self.timestamp_display_methods = []
        for field in self.model_admin.timestamp_fields:
            self.timestamp_display_methods.append(
                self.create_list_display(field))
        self.add_timestamps_to_list_display()

    def add_timestamps_to_list_display(self):
        """
        Appends the created and modified fields to the list display, unless
        they are already in there.
        """
        for method in self.timestamp_display_methods:
            self.list_display.append(method)

    def get_timestamp_verbose_name(self, field):
        """
        Get the accessor name as configured using the model admin's
        ``timestamp_fields`` attribute.
        """
        return self.model._meta.get_field(field).verbose_name

    def get_timestamp(self, obj, field):
        """
        Get either the created or modified datetime from the model.
        """
        if hasattr(obj, field):
            return getattr(obj, field)

    def create_list_display(self, field):
        """
        Create a timestamp list_display method.
        """
        method = lambda obj: human_timestamp(self.get_timestamp(obj, field))
        method.admin_order_field = field
        method.short_description = self.get_timestamp_verbose_name(field)
        return method


class TimestampedAdminMixin(object):
    """
    This mixin adds custom display of timestamp fields to the Django
    admin changelist.
    """

    timestamp_fields = DEFAULT_TIMESTAMP_FIELDS

    def get_changelist(self, request, **kwargs):
        """
        Hands back the custom changelist implementation.
        """
        ChangeList = (super(TimestampedAdminMixin, self)
                      .get_changelist(request, **kwargs))
        return type('%s$TimestampedChangelist' % self.__class__.__name__,
                    (TimestampedChangelist, ChangeList), {})
