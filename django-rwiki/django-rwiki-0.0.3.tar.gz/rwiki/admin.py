# -*- coding: utf-8 -*-

from django.contrib import admin
import models as mymodels
import forms as myforms
import socket
import reversion

class AdminPage(reversion.VersionAdmin):
    #exclude = ('user',)

    # http://www.userlinux.net/django-los-campos-tipo-slug.html
    prepopulated_fields = { 'slug': ['title'] }

class AdminCategory(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ['title'] }

admin.site.register(mymodels.Page, AdminPage)
