from django.contrib import admin

from ella_attachments.models import Attachment, Type


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'created',)
    list_filter = ('type',)
    prepopulated_fields = {'slug': ('name',)}
    rich_text_fields = {'small': ('description',)}
    # If you want publistable prompter you must register admin for this
    raw_id_fields = ('photo', 'publishables',)


class TypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Type, TypeAdmin)
