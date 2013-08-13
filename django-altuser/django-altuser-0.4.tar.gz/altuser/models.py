from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist 
from django.contrib.auth.models import (AbstractBaseUser,
                                PermissionsMixin,
                                BaseUserManager)
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.utils.http import urlquote
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django.conf import settings

def _getSettingKey(key, default):
    """
    Get a key's value defined in settings
    """
    getattr(settings, key, default)


class MailUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.

        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = MailUserManager.normalize_email(email)
        user = self.model(email=email,
                          is_staff=False, is_active=True, is_superuser=False,
                          last_login=now, date_joined=now, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        u = self.create_user(email, password, **extra_fields)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u


class AbstractMailUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing fully featured User model with
    admin-compliant permission

    Email, password and email are required. Email is identifying the User and it is unique.
    """

    email = models.EmailField(_('email'), max_length=254, unique=True,
                              help_text=_('Required. Email field'),
                              error_messages={'unique': _('This email is not available, choose another one')} )
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_modified = models.DateTimeField(_('last modified'), auto_now=True)

    # This three fields permits to have a related 
    # profile associated with this user
    profile_type = models.ForeignKey(ContentType, null=True, blank=True)
    profile_id = models.PositiveIntegerField(blank=True, null=True)
    profile = generic.GenericForeignKey('profile_type', 'profile_id')

    objects = MailUserManager()
    
    USERNAME_FIELD = 'email'

    def __unicode__(self):
        return self.email

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.username)

    def get_full_name(self):
        try:
            return str(self.get_profile())
        except:
            return self.email

    def get_short_name(self):
        "Returns the short name for the user."
        return self.email.split("@")[0]

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def get_profile(self):
        if self.profile is not None:
            return self.profile
        else:
            try:
                # altuser profiles is a list of reverse relation names
                # of what could be your different site profiles
                for p in settings.ALTUSER_PROFILES_BREL:
                    try:
                        return getattr(self, p)
                    except ObjectDoesNotExist:
                        pass
            except AttributeError:
                # if ALTUSER_PROFILES_BREL does not exists
                pass
        raise NotImplementedError('Not implemented')

    @staticmethod
    def generate_username():
        import uuid
        return uuid.uuid4().hex + "@example.com"

class AbstractMailConfirmedUser(AbstractMailUser):
    """
    Not usable per se but you need to use it as a mixin
    """
    from django.contrib.contenttypes import generic
    from mail_confirmation.models import MailConfirmation
    from mail_confirmation.utils import generate_and_send

    confirmed = generic.GenericRelation(MailConfirmation,
                                        content_type_field='toconfirm_type',
                                        object_id_field='toconfirm_id')

    
    def create_user(self, email, password=None, **extra_fields):
        user = super(AbstractMailConfirmedUser, self).create_user(email, password, **extra_fields)
        generate_and_send(user, 
                          _('User registration confirmation'),to=user.email, 
                          )
        return user
        
    class Meta:
        abstract = True


class MailUser(AbstractMailUser):
    """
    User model with email as required identification field and without username.

    Email and password are required.
    """
    class Meta:
        swappable = 'AUTH_USER_MODEL'


class MailSocialUser(AbstractMailUser):
    """
    User model with email as required identification field and without username.

    Email and password are required.
    It also provides follows and likes fields to track this kind of user interaction.
    """
    likes = models.ManyToManyField('self', related_name='liked', symmetrical=False)
    follows = models.ManyToManyField('self', related_name='followed', symmetrical=False)
    class Meta:
        swappable = 'AUTH_USER_MODEL'


class MailConfirmedUser(AbstractMailConfirmedUser):
    """
    User model with email as required identification field and without username.

    Email and password are required.
    
    Uses email as confirmation to the user subscription
    """
    class Meta:
        swappable = 'AUTH_USER_MODEL'


class MailConfirmedSocialUser(AbstractMailConfirmedUser):
    """
    User model with email as required identification field and without username.

    Email and password are required.
    It also provides follows and likes fields to track this kind of user interaction.

    Uses email as confirmation to the user subscription
    """
    likes = models.ManyToManyField('self', related_name='liked', symmetrical=False)
    follows = models.ManyToManyField('self', related_name='followed', symmetrical=False)
    class Meta:
        swappable = 'AUTH_USER_MODEL'
