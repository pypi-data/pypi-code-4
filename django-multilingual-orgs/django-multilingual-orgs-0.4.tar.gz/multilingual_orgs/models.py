"""Models for the ``multilingual_orgs`` app."""
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models.pluginmodel import CMSPlugin
from django_libs.models_mixins import (
    SimpleTranslationMixin,
    SimpleTranslationPublishedManager,
)
from filer.fields.file import FilerFileField

from . import settings


class Organization(SimpleTranslationMixin, models.Model):
    """
    Holds information about an organization.

    :logo: The image file that contains the logo of the organization.
    :website: URL of the website.
    :phone: The phone number of that organization.

    """

    logo = FilerFileField(
        verbose_name=_('Logo'),
        blank=True, null=True,
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

    objects = SimpleTranslationPublishedManager()

    def __unicode__(self):
        return self.get_translation().title


class OrganizationPersonRole(models.Model):
    """
    Intermediary model to connect an organization to a person from
    django-people.

    :organization: The organization the person belongs to.
    :person: The person that belongs to that initiative.
    :role: The role of that person inside the organization.
    :position: An integer for ordering.

    """

    organization = models.ForeignKey(
        Organization,
        verbose_name=_('Organization'),
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


class OrganizationPluginModel(CMSPlugin):
    """
    Model for the ``OrganizationPluginModel`` cms plugin.

    :display_type: The way the plugin is displayed. E.g. 'big' or 'small'
    :organization: The organization this plugin shows.

    """
    display_type = models.CharField(
        max_length=256,
        choices=settings.DISPLAY_TYPE_CHOICES,
        verbose_name=_('Display type'),
    )

    organization = models.ForeignKey(
        Organization,
        verbose_name=_('Organization'),
    )


class OrganizationTranslation(models.Model):
    """
    Translatable fields of the ``Organization`` model.

    :title: The title of the organization.
    :is_published: If the translation of this organization is published or not.

    Needed by simple translation:
    :language: The language code for this translation. E.g. 'en'
    :organization: The organization this is the translation of.

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

    organization = models.ForeignKey(
        'multilingual_orgs.Organization',
        verbose_name=_('Organization'),
    )
