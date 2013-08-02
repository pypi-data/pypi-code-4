# coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.utils.datetime_safe import datetime
from django.contrib.sessions.models import Session
from django_helpers import get_ip_address_from_request


class LoginHistoryManager(models.Manager):
    @property
    def active_sessions(self):
        return self.filter(session__expire_date__gte=datetime.now())

    @property
    def expired_sessions(self):
        return self.filter(session__expire_date__lt=datetime.now())

    def get_history(self, user):
        return self.active_sessions.filter(user=user)


class LoginHistory(models.Model):
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.IPAddressField(null=True)
    session = models.ForeignKey(Session)
    user_agent = models.CharField(max_length=255, blank=True)

    objects = LoginHistoryManager()

    def logout(self):
        self.session.delete()

# Connect signal
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in


@receiver(user_logged_in)
def save_login_history(request, user):
    history = LoginHistory()
    history.user = user
    history.ip_address = get_ip_address_from_request(request)
    history.session = request.session
    history.user_agent = request.META['HTTP_USER_AGENT']
    history.save()
