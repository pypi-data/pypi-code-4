# coding=utf-8
from django.forms import fields
from django.utils import formats
from django.utils.safestring import mark_safe

from . import Widget, js_bool, js_date
from django_helpers.helpers.views import render_to_string
from django_helpers.apps.static_manager import BootstrapURL, jQueryURL


class FormatNotAllowedException(Exception):
    def __init__(self, formats, part):
        msg = '"%s" is not allowed in this date format.\nAllowed formats are %s' % (part, formats)
        Exception.__init__(self, msg)


def _date_format_converter(django_date_format, formats):
    i = 0
    l = len(django_date_format)
    new_format = ''
    while i < l:
        first_letter = django_date_format[i]
        # If the character does not starts with %
        # Then its not a date format section.
        if first_letter != '%':
            new_format += first_letter
            i += 1
        else:
            # Python date formats are always two
            # characters with % as a start.
            section = django_date_format[i:i + 2]
            if section not in formats:
                if section == "%%":
                    new_format += "%"
                else:
                    raise FormatNotAllowedException(formats.keys(), section)
            else:
                new_format += formats[section]
            i += 2
    return new_format


def moment_date_format(django_date_format):
    """
    Django : http://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
    Bootstrap : http://momentjs.com/docs/#/parsing/string-format/
    @param django_date_format:
    @return:
    """
    formats = {
        '%a': 'ddd',
        '%A': 'dddd',
        '%b': 'MMM',
        '%B': 'MMMM',
        '%d': 'DD',
        '%H': 'HH',
        '%I': 'hh',
        '%j': 'DDDD',
        '%m': 'MM',
        '%M': 'mm',
        '%p': 'A',
        '%S': 'ss',
        '%w': 'd',
        '%W': 'w',
        '%y': 'YY',
        '%Y': 'YYYY',
    }
    return _date_format_converter(django_date_format, formats)


class BootstrapDateFormatMixin():
    def js_date_format(self, date_format=None):
        """
        var val = {
                d: date.getUTCDate(),

                D: dates[language].daysShort[date.getUTCDay()],
                DD: dates[language].days[date.getUTCDay()],

                m: date.getUTCMonth() + 1,

                M: dates[language].monthsShort[date.getUTCMonth()],
                MM: dates[language].months[date.getUTCMonth()],

                yy: date.getUTCFullYear().toString().substring(2),
                yyyy: date.getUTCFullYear()
            };

        val.dd = (val.d < 10 ? '0' : '') + val.d;
        val.mm = (val.m < 10 ? '0' : '') + val.m;
        @return: Django date format converted to js format.
        """

        formats = {
            '%d': 'd',
            '%a': 'D',
            '%A': 'DD',
            '%m': 'm',
            '%b': 'M',
            '%B': 'MM',
            '%y': 'yy',
            '%Y': 'yyyy'
        }
        date_format = getattr(self, 'format', date_format)
        if date_format is None:
            raise Exception('Date format does not exists.')
        return _date_format_converter(date_format, formats)


# noinspection PyShadowingBuiltins
class DatePickerWidget(Widget, fields.DateInput, BootstrapDateFormatMixin):
    def __init__(self, attrs=None, format=None, week_start=0, calendar_weeks=False,
                 start_date=None, end_date=None, day_of_week_disabled=None, auto_close=False,
                 start_view=0, min_view_mode=0, today_btn=False, today_highlight=False,
                 keyboard_navigation=True, language='en', force_parse=True):
        fields.DateInput.__init__(self, attrs, format)

        self.js_files = [jQueryURL, BootstrapURL, 'js/moment.min.js', 'js/bootstrap-datepicker.js']

        self.week_start = week_start
        self.calendar_weeks = calendar_weeks
        self.start_date = start_date
        self.end_date = end_date
        self.day_of_week_disabled = day_of_week_disabled
        self.auto_close = auto_close
        self.start_view = start_view
        self.min_view_mode = min_view_mode
        self.today_btn = today_btn
        self.today_highlight = today_highlight
        self.keyboard_navigation = keyboard_navigation
        self.language = language
        self.force_parse = force_parse

    def render_js(self):
        return render_to_string('django-helpers/forms/bootstrap-date-picker.js', {
            "week_start": self.week_start,
            "calendar_weeks": js_bool(self.calendar_weeks),
            "id": self.html_id,
            "format": self.js_date_format(),
            "start_date": js_date(self.start_date),
            "end_date": js_date(self.end_date),
            "day_of_week_disabled": self.day_of_week_disabled,
            "auto_close": js_bool(self.auto_close),
            "start_view": self.start_view,
            "min_view_mode": self.min_view_mode,
            "today_btn": js_bool(self.today_btn),
            "today_highlight": js_bool(self.today_highlight),
            "keyboard_navigation": js_bool(self.keyboard_navigation),
            "language": self.language,
            "force_parse": js_bool(self.force_parse)
        })


# noinspection PyShadowingBuiltins
class ClockFaceWidget(Widget, fields.TimeInput):
    def __init__(self, attrs=None, format='H:mm', trigger='focus'):
        fields.TimeInput.__init__(self, attrs, format)

        self.js_files = [jQueryURL, BootstrapURL, 'js/clockface.js']

        self.trigger = trigger

    def js_date_format(self):
        formats = {
            '%H': 'HH',
            '%I': 'hh',
            '%M': 'mm',
            '%p': 'A'
        }
        return _date_format_converter(self.format, formats)

    def render_js(self):
        return render_to_string('django-helpers/forms/bootstrap-clock-face.js', {
            "id": self.html_id,
            "format": self.js_date_format(),
            "trigger": self.trigger
        })


# noinspection PyShadowingBuiltins
class DateTimePickerWidget(Widget, fields.DateTimeInput):
    def __init__(self, attrs=None, format=None, mask_input=True, pick_date=True,
                 pick_12_hour_format=False, pick_seconds=True, start_date=None, end_date=None):
        fields.DateTimeInput.__init__(self, attrs, format)
        self.js_files = [jQueryURL, BootstrapURL, 'js/bootstrap-datetimepicker.js']

        self.mask_input = mask_input
        self.pick_date = pick_date
        self.pick_12_hour_format = pick_12_hour_format
        self.pick_seconds = pick_seconds
        self.start_date = start_date
        self.end_date = end_date

    def js_date_format(self):
        """
          var dateFormatComponents = {
            dd: {property: 'UTCDate', getPattern: function() { return '(0?[1-9]|[1-2][0-9]|3[0-1])\\b';}},
            MM: {property: 'UTCMonth', getPattern: function() {return '(0?[1-9]|1[0-2])\\b';}},
            yy: {property: 'UTCYear', getPattern: function() {return '(\\d{2})\\b'}},
            yyyy: {property: 'UTCFullYear', getPattern: function() {return '(\\d{4})\\b';}},
            hh: {property: 'UTCHours', getPattern: function() {return '(0?[0-9]|1[0-9]|2[0-3])\\b';}},
            mm: {property: 'UTCMinutes', getPattern: function() {return '(0?[0-9]|[1-5][0-9])\\b';}},
            ss: {property: 'UTCSeconds', getPattern: function() {return '(0?[0-9]|[1-5][0-9])\\b';}},
            ms: {property: 'UTCMilliseconds', getPattern: function() {return '([0-9]{1,3})\\b';}},
            ms is not available in python
            HH: {property: 'Hours12', getPattern: function() {return '(0?[1-9]|1[0-2])\\b';}},
            PP: {property: 'Period12', getPattern: function() {return '(AM|PM|am|pm|Am|aM|Pm|pM)\\b';}}
          };



        """
        formats = {
            '%d': 'dd',
            '%m': 'MM',
            '%y': 'YY',
            '%Y': 'YYYY',
            '%H': 'hh',
            '%M': 'mm',
            '%S': 'ss',
            '%f': 'ms',
            '%I': 'HH',
            '%P': 'PP'
        }
        return _date_format_converter(self.format, formats)

    def render_js(self):
        return render_to_string('django-helpers/forms/bootstrap-date-time-picker.js', {
            "id": self.html_id,
            "format": self.js_date_format(),
            "mask_input": self.mask_input,

            "pick_date": js_bool(self.pick_date),
            "pick_12_hour_format": js_bool(self.pick_12_hour_format),
            "pick_seconds": js_bool(self.pick_seconds),

            "start_date": self.start_date,
            "end_date": self.end_date,

        })


# noinspection PyShadowingBuiltins
class ColorPickerWidget(Widget, fields.TextInput):
    def __init__(self, attrs=None, format='hex'):
        fields.TextInput.__init__(self, attrs)
        self.js_files = [jQueryURL, BootstrapURL, 'js/bootstrap-colorpicker.js']
        self.format = format

    def render_js(self):
        return render_to_string('django-helpers/forms/bootstrap-color-picker.js', {
            "id": self.html_id,
            "format": self.format,
        })


# noinspection PyShadowingBuiltins
class SelectWidget(Widget, fields.Select):
    def __init__(self, attrs=None, choices=(), button_class='btn', button_width='auto',
                 button_container=None, selected_class='active',
                 max_height=0, include_select_all_option=False, select_all_text=False, select_all_value=None,
                 enable_filtering=False, filter_placeholder='Search', drop_right=False):
        fields.Select.__init__(self, attrs, choices)
        self.js_files = [jQueryURL, BootstrapURL, 'js/bootstrap-multiselect.js']

        self.button_class = button_class
        self.button_width = button_width
        self.button_container = button_container
        self.selected_class = selected_class
        self.max_height = max_height
        self.include_select_all_option = include_select_all_option
        self.select_all_text = select_all_text
        self.select_all_value = select_all_value
        self.enable_filtering = enable_filtering
        self.filter_placeholder = filter_placeholder
        self.drop_right = drop_right

    def render_js(self):
        button_container = self.button_container
        if button_container is not None:
            button_container = mark_safe(self.button_container)

        return render_to_string('django-helpers/forms/bootstrap-multi-select.js', {
            "id": self.html_id,
            "button_class": self.button_class,
            "button_width": self.button_width,
            "button_container": button_container,
            "selected_class": self.selected_class,
            "max_height": self.max_height,
            "include_select_all_option": js_bool(self.include_select_all_option),
            "select_all_text": self.select_all_text,
            "select_all_value": self.select_all_value,
            "enable_filtering": js_bool(self.enable_filtering),
            "filter_placeholder": self.filter_placeholder,
            "drop_right": js_bool(self.drop_right)
        })


# noinspection PyShadowingBuiltins
class MultiSelectWidget(SelectWidget, fields.SelectMultiple):
    pass


# noinspection PyShadowingBuiltins
class TimePickerWidget(Widget, fields.TimeInput):
    def __init__(self, attrs=None, format=None, mask_input=True, pick_12_hour_format=False, pick_seconds=True):
        fields.TimeInput.__init__(self, attrs, format)
        self.js_files = [jQueryURL, BootstrapURL, 'js/bootstrap-datetimepicker.js']

        self.mask_input = mask_input
        self.pick_date = False
        self.pick_12_hour_format = pick_12_hour_format
        self.pick_seconds = pick_seconds
        # self.start_date = start_date
        # self.end_date = end_date

    def js_date_format(self):
        """
          var dateFormatComponents = {
            dd: {property: 'UTCDate', getPattern: function() { return '(0?[1-9]|[1-2][0-9]|3[0-1])\\b';}},
            MM: {property: 'UTCMonth', getPattern: function() {return '(0?[1-9]|1[0-2])\\b';}},
            yy: {property: 'UTCYear', getPattern: function() {return '(\\d{2})\\b'}},
            yyyy: {property: 'UTCFullYear', getPattern: function() {return '(\\d{4})\\b';}},

            hh: {property: 'UTCHours', getPattern: function() {return '(0?[0-9]|1[0-9]|2[0-3])\\b';}},
            mm: {property: 'UTCMinutes', getPattern: function() {return '(0?[0-9]|[1-5][0-9])\\b';}},
            ss: {property: 'UTCSeconds', getPattern: function() {return '(0?[0-9]|[1-5][0-9])\\b';}},
            ms: {property: 'UTCMilliseconds', getPattern: function() {return '([0-9]{1,3})\\b';}},
            HH: {property: 'Hours12', getPattern: function() {return '(0?[1-9]|1[0-2])\\b';}},
            PP: {property: 'Period12', getPattern: function() {return '(AM|PM|am|pm|Am|aM|Pm|pM)\\b';}}
          };



        """
        formats = {
            '%H': 'hh',
            '%M': 'mm',
            '%S': 'ss',
            '%f': 'ms',
            '%I': 'HH',
            '%P': 'PP'
        }
        return _date_format_converter(self.format, formats)

    def render_js(self):
        return render_to_string('django-helpers/forms/bootstrap-date-time-picker.js', {
            "id": self.html_id,
            "format": self.js_date_format(),
            "mask_input": self.mask_input,

            "pick_date": js_bool(False),
            "pick_12_hour_format": js_bool(self.pick_12_hour_format),
            "pick_seconds": js_bool(self.pick_seconds),

            # "start_date": self.start_date,
            # "end_date": self.end_date,

        })


# noinspection PyShadowingBuiltins
class DateRangeInputWidget(Widget, fields.TextInput):
    def __init__(self, attrs=None, format=None):
        fields.TextInput.__init__(self, attrs)
        if format is None:
            self.format = formats.get_format('DATE_INPUT_FORMATS')[0]
        else:
            self.format = format

        self.js_files = [jQueryURL, BootstrapURL, 'js/daterangepicker.js']

    def render_js(self):
        return render_to_string('django-helpers/forms/bootstrap-date-range.js', {
            "id": self.html_id,
            "format": moment_date_format(self.format),
        })


class SwitchWidget(Widget, fields.CheckboxInput):
    def __init__(self, attrs=None, check_test=None, on_label=None, off_label=None, on_icon=None, off_icon=None):
        fields.CheckboxInput.__init__(self, attrs, check_test)
        self.js_files = [jQueryURL, BootstrapURL, 'js/bootstrapSwitch.js']

        self.on_label = on_label if on_label is not None else ''
        self.off_label = off_label if off_label is not None else ''

        if on_icon is not None:
            self.on_label = "<i class='icon-%s'></i>" % on_icon

        if off_icon is not None:
            self.off_label = "<i class='icon-%s'></i>" % off_icon

    def render_js(self):
        return render_to_string('django-helpers/forms/bootstrap-switch.js', {
            "id": self.html_id,
            'yes': self.on_label,
            'no': self.off_label
        })