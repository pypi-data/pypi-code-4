from django.db import models
import random

from django.conf import settings
try:
    storage = settings.MULTI_IMAGES_FOLDER+'/'
except AttributeError:
    storage = 'multiuploader_images/'

class File(models.Model):
    """Model for storing uploaded photos"""
    filename = models.CharField(max_length=60, blank=True, null=True)
    image = models.FileField(upload_to=storage)
    key_data = models.CharField(max_length=90, unique=True, blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    @property
    def key_generate(self):
        """returns a string based unique key with length 80 chars"""
        while 1:
            key = str(random.getrandbits(256))
            try:
                File.objects.get(key=key)
            except:
                return key

    @property
    def extension(self):
        splited_filename = self.image.name.split('.')
        if splited_filename:
            return splited_filename[-1]
        return ''

    @property
    def is_image(self):
        return self.extension.lower() in ['jpg', 'jpeg', 'png', 'gif']

    @property
    def is_epub(self):
        return self.extension == 'epub'
    
    @property
    def thumbnail_src(self):
        if self.is_image:
            src = self.image.url
        else:
            src = getattr(settings, "FILE_IMAGE_URL", '')
        return src

    def __unicode__(self):
        return self.image.name

