from django.db import models


class TimestampedItem(models.Model):
    title = models.CharField('title', max_length=100)
    created = models.DateTimeField('created', auto_now_add=True)
    modified = models.DateTimeField('modified', auto_now=True)

    def __unicode__(self):
        return self.title


class SingleTimestampedItem(models.Model):
    title = models.CharField('title', max_length=100)
    modified = models.DateTimeField('modified', auto_now=True)

    def __unicode__(self):
        return self.title


class DateStampedItem(models.Model):
    title = models.CharField('title', max_length=100)
    created = models.DateField('created', auto_now_add=True)
    modified = models.DateTimeField('modified', auto_now=True)

    def __unicode__(self):
        return self.title


class FakeTimestampedItem(models.Model):
    """
    This model doesn't actually set it's timestamps, makes it easier
    to get predictable and testable formatted output.
    """
    title = models.CharField('title', max_length=100)
    created = models.DateTimeField('created')
    modified = models.DateTimeField('modified')

    def __unicode__(self):
        return self.title


class AlternativeTimestampedItem(models.Model):
    title = models.CharField('title', max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title

class NullTimestampedItem(models.Model):
    """
    This model doesn't actually set it's timestamps, makes it easier
    to get predictable and testable formatted output.
    """
    title = models.CharField('title', max_length=100)
    created = models.DateTimeField('created', null=True, blank=True)
    modified = models.DateTimeField('modified', null=True, blank=True)

    def __unicode__(self):
        return self.title
