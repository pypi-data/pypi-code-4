from django.db import models


class Log(models.Model):
    date = models.DateTimeField(auto_now=True)
    user = models.CharField(max_length=200)
    message = models.TextField()
    passed = models.BooleanField()
