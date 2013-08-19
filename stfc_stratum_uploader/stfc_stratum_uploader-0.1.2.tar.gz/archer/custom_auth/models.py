from django.core import validators
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager, SiteProfileNotAvailable
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.http import urlquote
import re
import warnings
from django.utils.translation import ugettext_lazy as _


class AbstractUser(AbstractBaseUser, PermissionsMixin):
    """
    This class is just a copy of default Django AbstractUser with couple changes to validation and field lengths.
    Copying all AbstractUser and User seemed to be better approach than any monkey patching.

    Username is a certificate DN so it has to allow characters like '/'.
    Additionally it is quite long so the length of username was increased to 200
    and might be change in the future if needed.


    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username, password and email are required. Other fields are optional.
    """
    username = models.CharField(_('username'), max_length=200, unique=True,
                                help_text=_('Required. 200 characters or fewer. Letters, numbers and '
                                            '@/./+/-/_//=/ characters'),
                                validators=[
                                    validators.RegexValidator(re.compile('^[\w.@+-=/ ]+$'), _('Enter a valid username.'), 'invalid')
                                ])
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.username)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def get_profile(self):
        """
        Returns site-specific profile for this user. Raises
        SiteProfileNotAvailable if this site does not allow profiles.
        """
        warnings.warn("The use of AUTH_PROFILE_MODULE to define user profiles has been deprecated.",
                      PendingDeprecationWarning)
        if not hasattr(self, '_profile_cache'):
            from django.conf import settings

            if not getattr(settings, 'AUTH_PROFILE_MODULE', False):
                raise SiteProfileNotAvailable(
                    'You need to set AUTH_PROFILE_MODULE in your project '
                    'settings')
            try:
                app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
            except ValueError:
                raise SiteProfileNotAvailable(
                    'app_label and model_name should be separated by a dot in '
                    'the AUTH_PROFILE_MODULE setting')
            try:
                model = models.get_model(app_label, model_name)
                if model is None:
                    raise SiteProfileNotAvailable(
                        'Unable to load the profile model, check '
                        'AUTH_PROFILE_MODULE in your project settings')
                self._profile_cache = model._default_manager.using(
                    self._state.db).get(user__id__exact=self.id)
                self._profile_cache.user = self
            except (ImportError, ImproperlyConfigured):
                raise SiteProfileNotAvailable
        return self._profile_cache


class User(AbstractUser):
    """
    This class is just a copy of default Django User with couple changes to validation and field lengths.
    Copying all AbstractUser and User seemed to be better approach than any monkey patching.

    Users within the Django authentication system are represented by this
    model.

    Username, password and email are required. Other fields are optional.
    """
    @classmethod
    def superuser_exist(cls):
        return User.objects.filter(is_superuser=True, is_staff=True).count() > 0

    class Meta:
        app_label = 'custom_auth'
        swappable = 'AUTH_USER_MODEL'
