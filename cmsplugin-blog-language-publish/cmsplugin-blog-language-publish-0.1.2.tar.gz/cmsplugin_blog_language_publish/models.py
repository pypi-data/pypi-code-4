"""Models for the ``cmsplugin_blog_language_publish`` app."""
from django.db import models
from django.utils.translation import ugettext_lazy as _


class EntryLanguagePublish(models.Model):
    """
    Holds the information about the published state of a certain language of
    an entry.

    :entry_title: FK to the EntryTitle.
    :is_published: The published state of the entry and this language.

    """

    entry_title = models.OneToOneField(
        'cmsplugin_blog.EntryTitle',
        verbose_name=_('Entry title'),
        related_name='is_published',
    )

    is_published = models.BooleanField(
        verbose_name=_('Published'),
        default=False,
    )
