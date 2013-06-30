from django.utils.translation import ugettext as _
from django.contrib import admin
from mptt.admin import FeinCMSModelAdmin
from django_zen.models import Menu, Page


class AppLabelAdminMixin(object):
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context['app_label'] = self.model._meta.app_label.title()
        return super(AppLabelAdminMixin, self).render_change_form(request, context, add, change, form_url, obj)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['app_label'] = self.model._meta.app_label.title()
        return super(AppLabelAdminMixin, self).changelist_view(request, extra_context)


class PagesAdmin(admin.ModelAdmin, AppLabelAdminMixin):
    list_display = ('url', 'title', 'published')

    def save_model(self, request, obj, form, change):
        obj.save()
        if form.cleaned_data['menu']:
            obj.menu.url = obj.url
            obj.menu.save()

    fieldsets = [
        (None, {'fields': ['url', 'title', 'template']}),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': ['menu', 'published']
        }),
        (_('Content'), {
            'classes': ('full-width',),
            'fields': ['content', ]
        }),
    ]


class MenuAdmin(FeinCMSModelAdmin, AppLabelAdminMixin):
    list_display = ('name', 'url', 'menu_id', 'published')

    fieldsets = [
        (None, {'fields': ['name', 'url', 'parent']}),
        (_('Menu settings'), {
            'classes': ('collapse',),
            'fields': ['menu_id', 'published']
        }),
    ]


admin.site.register(Menu, MenuAdmin)
admin.site.register(Page, PagesAdmin)
