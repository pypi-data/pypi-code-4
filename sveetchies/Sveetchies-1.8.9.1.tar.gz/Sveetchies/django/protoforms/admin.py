# -*- coding: utf-8 -*-
"""
Map des modèles de données dans l'administration de Django
"""
from django.contrib import admin

from models import SelectionItem

class SelectionItemAdmin(admin.ModelAdmin):
    list_display = ('key', 'label', 'kind', 'order', 'value_extended')
    list_filter = ('kind','value_extended')
    ordering = ('kind', 'order', 'label')
    search_fields = ('label',)

admin.site.register(SelectionItem, SelectionItemAdmin)