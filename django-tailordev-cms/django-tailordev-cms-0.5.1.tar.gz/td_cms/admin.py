# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext as _

from mptt.admin import MPTTModelAdmin
from modeltranslation.admin import TranslationAdmin
from reversion import VersionAdmin

from .models import Category, Page


class TinyMCEAdminMixin(object):
    group_fieldsets = True

    class Media:
        js = [
            '/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
            '/static/td_cms/javascripts/vendor/tinymce_setup.js',
        ]


class CategoryAdmin(TinyMCEAdminMixin, TranslationAdmin, MPTTModelAdmin):
    fieldsets = (
        (_("Base"), {'fields': ('name', 'parent', 'position',
                                'visible_in_menu')}),
        (_("Short description"), {'fields': ('short_description',)}),
        (_("Description"), {'fields': ('description',)}),
    )


class PageAdmin(TinyMCEAdminMixin, TranslationAdmin, VersionAdmin):
    fieldsets = (
        (_("Base"), {'fields': ('title', 'image', 'categories', 'status',
                                'is_highlighted', 'allow_comments',
                                'allow_sharing', 'position', 'author')}),
        (_("Synopsis"), {'fields': ('synopsis',)}),
        (_("Content"), {'fields': ('content',)}),
    )
    list_display = ('title', 'author', 'status', 'is_highlighted',
                    'creation_date', 'last_modified')
    list_display_links = ('title',)
    list_filter = ('status', 'creation_date', 'last_modified')
    actions = ['make_published', 'make_highlighted']

    def save_form(self, request, form, change):
        obj = super(PageAdmin, self).save_form(request, form, change)
        if not change:
            obj.author = request.user
        return obj

    # Actions
    def make_published(modeladmin, request, queryset):
        queryset.update(status='published')
    make_published.short_description = _("Mark selected pages as published")

    def make_highlighted(modeladmin, request, queryset):
        queryset.update(is_highlighted=True)
    make_highlighted.short_description = _("Mark selected pages as "
                                           "highlighted")


admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
