from django.contrib import admin

from dbtemplates.admin import TemplateAdmin as BaseTemplateAdmin
from dbtemplates.models import Template

from player.dbtemplate.forms import TemplateAdminForm

# deregistering legacy Template model admins
admin.site.unregister(Template)


class TemplateAdmin(BaseTemplateAdmin):
    form = TemplateAdminForm
    fieldsets = (
        (None, {
            'fields': ('name', 'content'),
            'classes': ('monospace',),
        }),
    )


admin.site.register(Template, TemplateAdmin)
