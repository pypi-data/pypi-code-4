from django.db import models
from django.contrib.auth.models import User

class DefaultManager(models.Manager):
    pass

class BadgeRecipientManager(models.Manager):

    def get_all_recipients(self):
        return User.objects.filter(badges__isnull=False).distinct()

    def get_all_nonrecipients(self):
        return User.objects.exclude(badges__isnull=False)

class Badge(models.Model):
    """
    Three fields:
        level - integer, default: 100
        name - text, max. 20 chars
        description - text, aim for one line

    receivers -> User.badges
    """
    level = models.PositiveIntegerField(default=100)
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    receivers = models.ManyToManyField(User, blank=True, null=True, related_name='badges')

    objects = BadgeRecipientManager()

    class Meta:
        db_table = 'nano_badge_badge'

    def __unicode__(self):
        return self.name

