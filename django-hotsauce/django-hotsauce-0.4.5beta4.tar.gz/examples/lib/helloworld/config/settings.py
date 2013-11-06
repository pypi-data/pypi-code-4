#Global settings for the helloworld app, to be overrided in local_settings.py.
from django.conf.global_settings import *
ROOT_URLCONF='helloworld.config.urls'
ENABLE_BEAKER=False
MEDIA_URL="/media/img/"
SECRET_KEY='12345va1110ht'
ENABLE_TIDYLIB=False
