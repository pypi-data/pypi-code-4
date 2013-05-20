from django.contrib import admin

from skypehub.models import Message


class MessageModelAdmin(admin.ModelAdmin):
    list_display = ('sender', 'chat_name', 'body', 'ctime')
    list_filter = ('chat_name', 'sender', 'ctime')
    search_fields = ('sender', 'chat_name', 'body')

admin.site.register(Message, MessageModelAdmin)
