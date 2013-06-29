from django.contrib import admin

from player.logicaldelete import admin as logicaldelete_admin
from player.data.models import CollectionGroup, Collection, CollectionField, Item


class CollectionGroupAdmin(admin.ModelAdmin):
    pass


class ItemAdmin(logicaldelete_admin.ModelAdmin):
    list_display = ('uid', 'collection', 'is_deleted', )
    list_filter = ('collection', 'is_deleted', )
    change_form_template = 'admin/data/item_change_form.html'


class CollectionFieldInline(admin.TabularInline):
    model = CollectionField
    prepopulated_fields = {"slug": ("name", )}


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'collectiongroup', )
    list_filter = ('collectiongroup', )
    inlines = (CollectionFieldInline, )


admin.site.register(CollectionGroup, CollectionGroupAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Item, ItemAdmin)
