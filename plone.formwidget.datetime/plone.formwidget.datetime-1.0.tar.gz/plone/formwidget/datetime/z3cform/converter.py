import pytz
from datetime import date, datetime
from plone.formwidget.datetime.z3cform.interfaces import DateValidationError
from plone.formwidget.datetime.z3cform.interfaces import\
    DatetimeValidationError
from z3c.form.converter import BaseDataConverter


class DateDataConverter(BaseDataConverter):

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return ('', '', '')
        return (value.year, value.month, value.day)

    def toFieldValue(self, value):
        for val in value:
            if not val:
                return self.field.missing_value

        try:
            value = map(int, value)
        except ValueError:
            raise DateValidationError
        try:
            return date(*value)
        except ValueError:
            raise DateValidationError


class DatetimeDataConverter(DateDataConverter):

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return ('', '', '', '00', '00', '')

        tz = getattr(value, 'tzinfo', '')
        if tz:
            tz = str(tz)
        else:
            tz = ''
        return (value.year,
                value.month,
                value.day,
                value.hour,
                value.minute,
                tz)

    def toFieldValue(self, value):
        if not value:
            return self.field.missing_value

        if len(value) > 5:
            # TZ component available
            dt_value = value[:-1]
            tz = value[-1]
        else:
            # TZ component not available
            dt_value = value
            tz = None

        for val in dt_value:
            if not val:
                return self.field.missing_value

        try:
            intvalues = map(int, dt_value)
        except ValueError:
            raise DatetimeValidationError

        try:
            if tz:
                # Timezone aware, localize.
                timezone = pytz.timezone(tz)
                return timezone.localize(datetime(*intvalues))
            else:
                # Timezone naive.
                return datetime(*intvalues)
        except ValueError:
            raise DatetimeValidationError


class MonthYearDataConverter(DateDataConverter):

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return ('', '', '1')
        return (value.year, value.month, value.day)


class YearDataConverter(DateDataConverter):

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return ('', '1', '1')
        return (value.year, value.month, value.day)
