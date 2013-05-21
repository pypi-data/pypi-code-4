# -*- coding: utf-8 -*-
from django.db import models


class Article(models.Model):
    title = models.CharField(
        max_length=1000, blank=True
    )
    annonce = models.TextField(blank=True)
    content = models.TextField(blank=True)