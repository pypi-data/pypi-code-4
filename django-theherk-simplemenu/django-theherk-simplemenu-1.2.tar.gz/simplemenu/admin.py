from django.contrib import admin
from simplemenu.models import SimpleMenu
from simplemenu.models import Link


class SimpleMenuAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Simple Menu', {
            'fields': ['name']
        }),
    ]
    list_display = ('name',)
    list_display_links = ('name',)
    search_fields = ['name']


class LinkAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Link', {
            'fields': [
                ('title', 'url',),
                'simplemenu'
            ]
        }),
    ]
    list_display = ('title', 'url')
    list_display_links = ('title', 'url')
    ordering = ('title',)
    list_filter = ('simplemenu__name',)
    search_fields = ['title']

admin.site.register(SimpleMenu, SimpleMenuAdmin)
admin.site.register(Link, LinkAdmin)
