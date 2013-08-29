#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.forms import TextInput, Select, MultiWidget
from django.utils.dates import MONTHS
from django.utils.translation import ugettext_lazy as _


MONTH_CHOICES_WITH_EMPTY = [("", _("Month"))] + sorted(MONTHS.items())
MONTH_CHOICES_WITH_PRESENT = [("", _("Present"))] + sorted(MONTHS.items())


class YearAndMonthWidget(MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            Select(attrs={"class": "span3"}),
            TextInput(attrs={"class": "span2", "placeholder": _("Year")}),
        )
        super(YearAndMonthWidget, self).__init__(widgets, attrs=attrs)

    def decompress(self, value):
        if value:
            return value.month, value.year
        return [None, None]

    def format_output(self, rendered_widgets):
        return super(YearAndMonthWidget, self).format_output(rendered_widgets)


class YearAndMonthField(forms.MultiValueField):
    widget = YearAndMonthWidget

    def get_choices(self, required):
        return MONTH_CHOICES_WITH_EMPTY

    def __init__(self, required=True, widget=None, label=None, initial=None, help_text=None):
        choices=self.get_choices(required)
        fields = (
             forms.ChoiceField(choices=choices),
             forms.IntegerField(min_value=1900, max_value=2050, required=required),
        )
        super(YearAndMonthField, self).__init__(fields=fields, widget=widget,
              label=label, initial=initial, help_text=help_text, required=required)
        self.widget.widgets[0].choices = choices

    def compress(self, data_list):
        if data_list:
            if data_list[1] and not data_list[0]:
                raise ValidationError(_("Provide month as well"))

            if data_list[0] and not data_list[1]:
                raise ValidationError(_("Provide year as well"))

        if data_list and all(data_list):
            return datetime.date(int(data_list[1]), int(data_list[0]), 1)


class YearAndMonthFieldWithPresent(YearAndMonthField):
    def get_choices(self, required):
        return MONTH_CHOICES_WITH_PRESENT
