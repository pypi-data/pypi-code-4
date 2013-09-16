from datetime import datetime
from django.db import models


class PublishedPictureManager(models.Manager):
    """
    PublishedPictureManager returns only published pictures
    """
    def get_query_set(self):
        today = datetime.now()
        return super(PublishedPictureManager, self).get_query_set().filter(published_at__lt=today)
