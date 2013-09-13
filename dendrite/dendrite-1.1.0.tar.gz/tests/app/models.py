from django.conf import settings
from django.db import models


class TestProfile(models.Model):
    id                 = models.CharField(max_length=255, primary_key=True)
    user               = models.ForeignKey(settings.AUTH_USER_MODEL)
    oauth_token        = models.CharField(max_length=255, blank=True)
    oauth_token_secret = models.CharField(max_length=255, blank=True)


class TwitterProfile(models.Model):
    user                  = models.ForeignKey(settings.AUTH_USER_MODEL)
    contributors_enabled  = models.BooleanField(blank=True, default=False)
    created_at            = models.CharField(max_length=255, blank=True)
    default_profile       = models.BooleanField(blank=True, default=True)
    default_profile_image = models.BooleanField(blank=True, default=True)
    description           = models.TextField(blank=True)
    favourites_count      = models.IntegerField(default=0, blank=True)
    follow_request_sent   = models.BooleanField(blank=True, default=True)
    following             = models.IntegerField(default=0, blank=True)
    followers_count       = models.IntegerField(default=0, blank=True)
    friends_count         = models.IntegerField(default=0, blank=True)
    geo_enabled           = models.BooleanField(blank=True, default=True)
    id_str                = models.CharField(max_length=255, blank=True)
    lang                  = models.CharField(max_length=255, blank=True)
    location              = models.CharField(max_length=255, blank=True)
    name                  = models.CharField(max_length=255, blank=True)
    protected             = models.BooleanField(blank=True, default=False)
    screen_name           = models.CharField(max_length=255, blank=True)
    verified              = models.BooleanField(blank=True, default=True)

    oauth_token           = models.CharField(max_length=255, blank=True)
    oauth_token_secret    = models.CharField(max_length=255, blank=True)
