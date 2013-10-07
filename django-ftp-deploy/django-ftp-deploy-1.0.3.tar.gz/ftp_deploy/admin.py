from django.contrib import admin
from django.utils.html import strip_tags

from .models import Log


class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'user', 'messageShortcut', 'passed')
    readonly_fields = ('date', 'user', 'message', 'passed')

    def messageShortcut(self, obj):
        if len(obj.message) > 220:
            return '%s...' % strip_tags(obj.message[:220].rstrip())
        else:
            return obj.message
    messageShortcut.short_description = 'Message'

    def has_add_permission(self, request):
        return False

admin.site.register(Log, LogAdmin)
