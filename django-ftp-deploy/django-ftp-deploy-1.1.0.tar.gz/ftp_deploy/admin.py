from django.contrib import admin

from .models import Log, Service


class ServiceAdmin(admin.ModelAdmin):

    list_display = ('repo_name', 'repo_branch', 'hook_url', 'status_message_html', 'status')
    fieldsets = (
        ('FTP Settings', {
            'fields': ('ftp_host', ('ftp_username', 'ftp_password'), 'ftp_path')
        }),
        ('Repository', {
            'classes': ('',),
            'fields': ('repo_source', 'repo_name', 'repo_branch')
        }),
        ('Security', {
            'classes': ('collapse',),
            'fields': ('secret_key',)
        }),
    )

    def status_message_html(self, obj):
        return obj.status_message
    status_message_html.allow_tags = True
    status_message_html.short_description = 'Status Message'


class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'user', 'status_message_html', 'status')
    readonly_fields = ('service', 'created', 'user', 'status')
    exclude = ('payload',)

    def has_add_permission(self, request):
        return False

    def status_message_html(self, obj):
        return obj.status_message
    status_message_html.allow_tags = True
    status_message_html.short_description = 'Status Message'

admin.site.register(Service, ServiceAdmin)
admin.site.register(Log, LogAdmin)
