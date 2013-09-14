from django.db import models


class SingletonBaseModel(models.Model):
    class Meta:
        abstract = True
