# -*- coding: utf8 -*-
from django.contrib import admin
from memento.models import LogEntry, LogEvent


class LogEventInline(admin.TabularInline):
    model = LogEvent
    readonly_fields = ('timestamp',)
    extra = 0


class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('message', 'object_as_string', 'count', 'severity', 'last_timestamp')
    readonly_fields = ('message', 'severity', 'last_timestamp')
    fields = ('message', 'severity', 'last_timestamp')
    inlines = [LogEventInline]

    def has_add_permission(self, request):
        return False

admin.site.register(LogEntry, LogEntryAdmin)