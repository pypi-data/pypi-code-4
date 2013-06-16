# coding=utf-8
from django.contrib.humanize.templatetags.humanize import naturaltime, ordinal, intcomma, naturalday
from . import DataTableColumn
from django.utils.html import linebreaks


class NaturalTimeColumn(DataTableColumn):
    def get_html(self, request, instance):
        value = DataTableColumn.get_html(self, request, instance)
        return naturaltime(value)


class NaturalDayColumn(DataTableColumn):
    def get_html(self, request, instance):
        value = DataTableColumn.get_html(self, request, instance)
        return naturalday(value)


class OrdinalIntegerColumn(DataTableColumn):
    def get_html(self, request, instance):
        value = DataTableColumn.get_html(self, request, instance)
        return ordinal(value)

class LineBreaksColumn(DataTableColumn):
    def get_html(self, request, instance):
        value = DataTableColumn.get_html(self, request, instance)
        return linebreaks(value)


class ComaSeparatedIntegerColumn(DataTableColumn):
    def get_html(self, request, instance):
        value = DataTableColumn.get_html(self, request, instance)
        return intcomma(value)