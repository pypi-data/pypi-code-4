# -*- coding: utf-8 -*-
"""
Map des modèles de données dans l'administration de Django
"""
from django.contrib import admin

from models import Template, History

class TemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'key', 'modified',)
    ordering = ('key',)
    search_fields = ('title',)
    fieldsets = (
        (u'Paramètres', {
            'classes': ('collapse',),
            'fields': ('key', 'title')
        }),
        (u'Message', {
            'fields': ('subject', 'body',)
        }),
    )

class HistoryAdmin(admin.ModelAdmin):
    list_display = ('sended', 'to_email', 'from_email', 'template',)
    list_filter = ('sended','template',)
    ordering = ('-sended',)
    raw_id_fields = ('template',)
    search_fields = ('to_email','from_email','subject','body',)

admin.site.register(Template, TemplateAdmin)
admin.site.register(History, HistoryAdmin)
