from django.db import models
from model_utils.managers import InheritanceManager


class Stream(models.Model):
    slug = models.SlugField()

    def __unicode__(self):
        return self.slug


class StreamItem(models.Model):
    stream = models.ForeignKey(Stream, related_name='items')
    pub_date = models.DateTimeField()

    objects = InheritanceManager()
