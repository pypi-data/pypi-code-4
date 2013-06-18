# -*- coding: utf-8 -*-

from django.contrib.admin.options import ModelAdmin
from django.contrib import admin

from .models import Country, Currency, Region, CountryGroup

class CountryGroupInline(admin.StackedInline):
    model = CountryGroup
    extra = 1

class RegionAdmin(ModelAdmin):
    inlines = [CountryGroupInline,]

class CountryAdmin(ModelAdmin):
    list_display = ('title', 'code', 'abbreviation', 'locale', 'vat_rate', 'tax_mode', 'is_primary')
    search_fields = ('title',)
    list_filter = ('title', 'is_primary',)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [CountryGroupInline,]

class CurrencyAdmin(ModelAdmin):
    list_display = ('title', 'code', 'code_position', 'symbol', 'symbol_position', 'short', 'short_position', 'mode')
    search_fields = ('title', 'code', 'symbol', 'short')


admin.site.register(Region, RegionAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Currency, CurrencyAdmin)