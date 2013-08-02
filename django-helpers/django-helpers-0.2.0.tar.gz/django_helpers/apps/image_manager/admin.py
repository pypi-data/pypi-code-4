# coding=utf-8
__author__ = 'ajumell'

from django.contrib.admin import site
from models import Image, ImageGroup

site.register(Image)
site.register(ImageGroup)
