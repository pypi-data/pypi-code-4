from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django_queue_mailer.models import Attachment, Queue, Log


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0


class QueueAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'to_address', 'deferred', 'app', 'created')
    list_filter = ('app', 'deferred')
    search_fields = ['to_address', 'subject', 'app', 'bcc_address']
    actions = ['send_failed']
    inlines = [AttachmentInline]

    def send_failed(self, request, queryset):
        emails = queryset.filter(sent=False)
        for email in emails:
            email.send_mail()
        self.message_user(request, _("Emails queued."))
    send_failed.short_description = _("Send failed")
admin.site.register(Queue, QueueAdmin)


class LogAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'subject', 'to_address', 'app', 'sent')
    list_filter = ('app',)
    search_fields = ['to_address', 'subject', 'app', 'bcc_address']
admin.site.register(Log, LogAdmin)