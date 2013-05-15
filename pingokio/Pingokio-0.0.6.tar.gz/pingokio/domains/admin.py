#-*- coding:utf-8 -*-
from django.contrib import admin

from domains.models import Domain, AvailabilityTestCase, CheckLog


class AvailabilityTestCaseInline(admin.TabularInline):
    model = AvailabilityTestCase


class DomainAdmin(admin.ModelAdmin):
    inlines = [AvailabilityTestCaseInline]


class CheckLogAdmin(admin.ModelAdmin):
    list_display = ('atc', 'status')


admin.site.register(Domain, DomainAdmin)
admin.site.register(CheckLog, CheckLogAdmin)
