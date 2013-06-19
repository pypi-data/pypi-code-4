# coding=utf-8
from django.core.files.storage import get_storage_class
from django_helpers import get_settings_val, check_settings_val_exist

__author__ = 'ajumell'

from django.db import models

check_settings_val_exist('MEDIA_ROOT')
check_settings_val_exist('MEDIA_URL')

STORAGE = get_storage_class(get_settings_val('FILE_MANAGER_STORAGE', None))
UPLOAD_TO = get_settings_val('FILE_MANAGER_FOLDER', 'image-manager/')

class File(models.Model):
    name = models.SlugField(max_length=100, unique=True)
    small_description = models.CharField(max_length=255, blank=True)
    large_description = models.TextField(blank=True)
    file = models.FileField(upload_to=UPLOAD_TO, storage=STORAGE())
    folder = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return self.name

    @property
    def url(self):
        return self.file.url


class FileGroup(models.Model):
    name = models.SlugField(max_length=255)
    files = models.ManyToManyField(File)


    def __unicode__(self):
        return self.name