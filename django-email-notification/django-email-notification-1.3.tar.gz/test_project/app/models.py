from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class Information(models.Model):
    title = models.CharField(max_length=100)

    def __unicode__(self):
        return self.title
