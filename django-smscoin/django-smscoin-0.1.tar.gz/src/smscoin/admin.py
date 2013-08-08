### -*- coding: utf-8 -*- ####################################################

from django.contrib import admin

from .models import Provider


class CountryAdmin(admin.ModelAdmin):
    list_display = ('country', 'name', 'number', 'prefix', 'price',)
    search_fields = ('country', 'name')
    
admin.site.register(Provider, CountryAdmin)
