from __future__ import unicode_literals
from django.db import models

from nodetree.models import BaseContent

class Town(BaseContent):

    name = models.CharField(max_length=63)


class Area(BaseContent):

    name = models.CharField(max_length=63)


class House(BaseContent):

    name = models.CharField(max_length=63)


class Person(BaseContent):

    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)