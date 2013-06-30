from django.utils.translation import ugettext as _
from django.contrib import admin
from mptt.admin import FeinCMSModelAdmin
from django_zen.models import Menu, Page


class PagesAdmin(admin.ModelAdmin):
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


class MenuAdmin(FeinCMSModelAdmin):
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
