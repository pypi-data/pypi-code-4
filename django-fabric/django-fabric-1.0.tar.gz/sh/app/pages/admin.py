# -*- coding: utf-8 -*-
from django.contrib import admin
from sh.app.pages.models import Category, Page

admin.site.register(Category)
admin.site.register(Page)