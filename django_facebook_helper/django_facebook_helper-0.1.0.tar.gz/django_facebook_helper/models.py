from django.db import models
from django.contrib.auth.models import User




class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    access_token = models.CharField(max_length=103, unique=True)
    expires = models.IntegerField(null=True)
    uid = models.BigIntegerField(unique=True, null=True)
        
    class Meta:
        unique_together = (('user', 'uid'), ('access_token', 'access_token'))
        
    def __unicode__(self):
        return u'Session for %s ' % self.user


User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])