# coding=utf-8
#
# Copyright (c) 2008-2013 by zenzire - http://www.zenzire.com
# Author Marcin Mierzejewski
#

from django.utils.translation import ugettext as _
from django.contrib import admin
from sorl.thumbnail import get_thumbnail
from sorl.thumbnail.admin import AdminImageMixin
from .models import Picture, Category, Tag


class PictureAdmin(AdminImageMixin, admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('published_at', 'admin_picture', 'description', 'is_published', 'category', 'admin_tags', 'views_counter', )   
    filter_horizontal = ("tags",)
    save_on_top = True
   
    def admin_tags(self, object):
        return ", ".join([tag.title for tag in object.tags.all()])
    admin_tags.short_description = _('Tags')
    
    def admin_picture(self, object):
        if object.picture:
            t = get_thumbnail(object.picture,"180x120", crop='center', quality=90)
            return u'<img src="%s" />' % t.url            

    admin_picture.short_description = _('Picture')
    admin_picture.allow_tags = True     
    
    def queryset(self, request):
        return Picture.objects.order_by('-published_at')

admin.site.register(Picture, PictureAdmin)


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('title',)

admin.site.register(Category, CategoryAdmin)


class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('title',)

admin.site.register(Tag, TagAdmin)

