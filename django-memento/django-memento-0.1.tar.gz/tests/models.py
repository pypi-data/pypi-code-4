from django.db import models


class Message(models.Model):
    string = models.CharField(max_length=50)