"""Models for the ``multilingual_initiatives`` app."""
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models.pluginmodel import CMSPlugin
from django_libs.models_mixins import SimpleTranslationMixin
from filer.fields.file import FilerFileField

from . import settings


class InitiativeManager(models.Manager):
    """Custom manager for the ``Initiative`` model."""
    def published(self, request, check_language=True):
        """
        Returns all initiatives, which are published and in the currently
        active language if check_language is True (default).

        :param request: A Request instance.
        :param check_language: Option to disable language filtering.

        """
        results = self.get_query_set().filter(
            initiativetranslation__is_published=True)
        if check_language:
            language = getattr(request, 'LANGUAGE_CODE', None)
            if not language:
                self.model.objects.none()
            results = results.filter(
                initiativetranslation__language=language)
        return results.distinct()


class Initiative(SimpleTranslationMixin, models.Model):
    """
    Holds information about an initiative.

    :logo: The image file that contains the logo of the initiative.
    :start_date: When the initiative starts.
    :end_date: When the initiative ends.
    :description: A short description of the initiative.
    :website: URL of the website.
    :phone: The phone number of that initiative. E.g. an information hotline
    :organization: The organization, that is responsible for the initiative.

    """

    logo = FilerFileField(
        verbose_name=_('Logo'),
        blank=True, null=True,
    )

    start_date = models.DateField(
        verbose_name=_('Start date'),
        blank=True, null=True,
    )

    end_date = models.DateField(
        verbose_name=_('End date'),
        blank=True, null=True,
    )

    description = models.CharField(
        verbose_name=_('Description'),
        max_length=160,
        blank=True,
    )

    website = models.URLField(
        verbose_name=_('Website'),
        blank=True,
    )

    phone = models.CharField(
        verbose_name=_('Phone'),
        max_length=128,
        blank=True,
    )

    organization = models.ForeignKey(
        'multilingual_orgs.Organization',
        verbose_name=_('Organization'),
        blank=True, null=True,
    )

    objects = InitiativeManager()

    def __unicode__(self):
        return self.get_translation().title


class InitiativePersonRole(models.Model):
    """
    Intermediary model to connect an initiative to a person from
    django-people.

    :initiative: The initiative the person belongs to.
    :person: The person that belongs to that initiative.
    :role: The role of that person inside the initiative.
    :position: An integer for ordering.

    """

    initiative = models.ForeignKey(
        Initiative,
        verbose_name=_('Initiative'),
    )

    person = models.ForeignKey(
        'people.Person',
        verbose_name=_('Person'),
    )

    role = models.ForeignKey(
        'people.Role',
        verbose_name=_('Role'),
        blank=True, null=True,
    )

    position = models.PositiveIntegerField(
        verbose_name=_('Position'),
        blank=True, null=True,
    )


class InitiativePluginModel(CMSPlugin):
    """
    Model for the ``InitiativePluginModel`` cms plugin.

    :display_type: The way the plugin is displayed. E.g. 'big' or 'small'
    :initiative: The initiative this plugin shows.

    """
    display_type = models.CharField(
        max_length=256,
        choices=settings.DISPLAY_TYPE_CHOICES,
        verbose_name=_('Display type'),
    )

    initiative = models.ForeignKey(
        Initiative,
        verbose_name=_('Initiative'),
    )


class InitiativeTranslation(models.Model):
    """
    Translatable fields of the ``Initiative`` model.

    :title: The title of the initiative.
    :is_published: If the translation of this initiative is published or not.

    Needed by simple translation:
    :language: The language code for this translation. E.g. 'en'
    :initiative: The initiative this is the translation of.

    """
    title = models.CharField(
        verbose_name=_('Title'),
        max_length=2000,
    )

    is_published = models.BooleanField(
        verbose_name=_('Is published'),
        default=False,
    )

    # Needed by simple translation
    language = models.CharField(
        verbose_name=_('Language'),
        max_length=16,
    )

    initiative = models.ForeignKey(
        'multilingual_initiatives.Initiative',
        verbose_name=_('Initiative'),
    )
