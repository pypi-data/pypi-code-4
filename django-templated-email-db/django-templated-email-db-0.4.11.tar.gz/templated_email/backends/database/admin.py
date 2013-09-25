from django.utils.translation import ugettext as _
from django.contrib import admin
from django import forms
from templated_email.backends.database.models import EmailTemplate
from templated_email.backends.database.widgets import CodeMirrorTextarea


class EmailTemplateAdminForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        widgets = {
            'text_message': CodeMirrorTextarea(mode='htmlembedded', theme='', config={'fixedGutter': True}),
            'html_message': CodeMirrorTextarea(mode='htmlembedded', theme='', config={'fixedGutter': True})
        }


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('subject', )
    form = EmailTemplateAdminForm

    fieldsets = [
        (None, {'fields': ['subject', ]}),
        (_('Text message'), {
            'classes': ('full-width',),
            'fields': ['text_message']
        }),
        (_('HTML message'), {
            'classes': ('full-width',),
            'fields': ['html_message', ]
        }),
    ]

admin.site.register(EmailTemplate, EmailTemplateAdmin)
