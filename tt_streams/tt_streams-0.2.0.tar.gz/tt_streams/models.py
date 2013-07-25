from django.db import models
from model_utils.managers import InheritanceManager


class Stream(models.Model):
    name = models.CharField(max_length=250)
    summary = models.TextField()
    slug = models.SlugField()

    def __unicode__(self):
        return self.name


class StreamItem(models.Model):
    stream = models.ForeignKey(Stream, related_name='items')
    pub_date = models.DateTimeField()

    objects = InheritanceManager()
