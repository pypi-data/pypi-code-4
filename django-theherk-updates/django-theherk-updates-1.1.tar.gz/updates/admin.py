from updates.models import Update
from updates.models import UpdateItem
from django.contrib import admin


class UpdateItemInline(admin.TabularInline):
    model = UpdateItem
    fieldsets = [
        ('About the Update', {
            'fields': ['item', 'description']
        }),
    ]
    extra = 1
    max_num = 10


class UpdateAdmin(admin.ModelAdmin):
    fieldsets = [
        ('When was the update?', {
            'fields': ['date']
        }),
    ]
    list_filter = ['date']
    inlines = [
        UpdateItemInline,
    ]

admin.site.register(Update, UpdateAdmin)
