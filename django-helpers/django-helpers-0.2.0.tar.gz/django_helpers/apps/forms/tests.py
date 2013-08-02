"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from widgets.bootstrap import DatePickerWidget


class JSFormatTestBase(TestCase):
    widget_class = None

    def test_format(self, date_format, excepted):
        widget = self.widget_class(format=date_format)
        self.assertEqual(excepted, widget.js_date_format())


class DatePickerJSFormatConvertion(JSFormatTestBase):
    widget_class = DatePickerWidget

    def test_basic_addition(self):
        self.test_format('', '')