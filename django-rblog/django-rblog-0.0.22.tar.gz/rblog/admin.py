# -*- coding: utf-8 -*-

from django.contrib import admin
from django.conf import settings as conf
import models as mymodels
import forms as myforms

def make_published(self, request, queryset):
    rows_updated = queryset.update(status=1)
    if rows_updated == 1:
        message_bit = "1 story was"
    else:
        message_bit = "%s stories were" % rows_updated
    self.message_user(request, "%s successfully marked as published." % message_bit)
make_published.short_description = "Mark selected stories as published"

def make_unpublished(self, request, queryset):
    rows_updated = queryset.update(status=0)
    if rows_updated == 1:
        message_bit = "1 story was"
    else:
        message_bit = "%s stories were" % rows_updated
    self.message_user(request, "%s successfully marked as unpublished." % message_bit)
make_unpublished.short_description = "Mark selected stories as unpublished"

class PostAdminForm(admin.ModelAdmin):

    list_display = ('title', 'user', 'creation_date', 'status')
    list_filter = ('user', 'creation_date')
    ordering = ('-creation_date',)
    search_fields = ('title','text',)
    actions = [make_published, make_unpublished]

    # http://www.userlinux.net/django-los-campos-tipo-slug.html
    prepopulated_fields = { 'slug': ['title'] }

    # http://www.userlinux.net/django-datos-del-usuario.html
    exclude = ('user',)

    # https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.filter%5Fhorizontal
    if "rgallery" in conf.INSTALLED_APPS:
        filter_horizontal = ['photo']

    # http://www.b-list.org/weblog/2008/dec/24/admin/
    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        obj.save()

    """
    Para agregar TinyMCE en los newforms-admin:
    - http://code.djangoproject.com/wiki/AddWYSIWYGEditor#Withnewforms-admin
    - http://code.djangoproject.com/wiki/AddWYSIWYGEditor
    """

    class Media:
        js = ('js/tiny_mce/tiny_mce.js',
              'js/textareas.js',
              )

admin.site.register(mymodels.Post, PostAdminForm)
admin.site.register(mymodels.Comments)
