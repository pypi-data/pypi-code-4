# coding: utf-8
from django.contrib import admin
from django_relinking.forms import LinkForm
from django_relinking.models import Link


class LinkAdmin(admin.ModelAdmin):

    search_fields = ['keys', 'content_type']
    list_display = ('keys', 'content_type', 'pk', 'direct_link')
    form = LinkForm


admin.site.register(Link, LinkAdmin)
