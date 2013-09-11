import datetime
import re
import hashlib
import random

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from templated_email import send_templated_mail

try:
    from django.utils.timezone import now as datetime_now
except ImportError:
    datetime_now = datetime.datetime.now


SHA1_RE = re.compile('^[a-f0-9]{40}$')


class AxtivationUserManagerMixin(object):
    def activate_user(self, activation_key):
        if SHA1_RE.search(activation_key):
            try:
                user = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not user.activation_key_expired():
                user.is_active = True
                user.activation_key = self.model.ACTIVATED
                user.save()
                return user
        return False

    def create_inactive_user(self, email, password, site, send_email=True):
        new_user = self.create_user(email, password)
        new_user.is_active = False
        new_user.activation_key = self.get_activation_key(new_user)
        new_user.save()

        if send_email:
            new_user.send_activation_email(site)

        return new_user
    create_inactive_user = transaction.commit_on_success(create_inactive_user)

    def get_activation_key(self, user):
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        email = user.email
        if isinstance(email, unicode):
            email = email.encode('utf-8')
        return hashlib.sha1(salt+email).hexdigest()

    def delete_expired_users(self):
        for user in self.all():
            if user.activation_key_expired():
                if not user.is_active:
                    user.delete()


class EmailUserManager(BaseUserManager, AxtivationUserManagerMixin):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves an EmailUser with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = EmailUserManager.normalize_email(email)
        user = self.model(email=email, is_staff=False, is_active=True,
                          is_superuser=False, last_login=now,
                          date_joined=now, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class AbstractEmailUser(AbstractBaseUser, PermissionsMixin):
    """
    Abstract User with the same behaviour as Django's default User but
    without a username field. Uses email as the USERNAME_FIELD for
    authentication.

    Use this if you need to extend EmailUser.

    Inherits from both the AbstractBaseUser and PermissionMixin.

    The following attributes are inherited from the superclasses:
        * password
        * last_login
        * is_superuser
    """
    ACTIVATED = u"ALREADY_ACTIVATED"

    email = models.EmailField(_('email address'), max_length=255,
                              unique=True, db_index=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    activation_key = models.CharField(_('activation key'), max_length=40)

    objects = EmailUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        abstract = True

    def get_full_name(self):
        """
        Returns the email.
        """
        return self.email

    def get_short_name(self):
        """
        Returns the email.
        """
        return self.email

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def activation_key_expired(self):
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == self.ACTIVATED or (self.date_joined + expiration_date <= datetime_now())
    activation_key_expired.boolean = True

    def send_activation_email(self, site):
        send_templated_mail(
            template_name='activation',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.email],
            context={
                'activation_key': self.activation_key,
                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                'site': site
            }
        )
