# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from rauthall.views import *

# Llamamos al registro a traves del formulario RegisterForm que hemos creado
urlpatterns = patterns('',

    # Accounts (Django-AllAuth)
    url(r'^', include('allauth.urls')),
    url(r'^profile/$', UserProfile.as_view(), {}, "app_rauthall-profile"),

)
