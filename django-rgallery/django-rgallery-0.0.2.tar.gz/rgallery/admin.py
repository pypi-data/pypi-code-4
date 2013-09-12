# -*- coding: utf-8 -*-

from django.contrib import admin
import models as mymodels
import forms as myforms
import socket

admin.site.register(mymodels.Photo)
admin.site.register(mymodels.Video)
