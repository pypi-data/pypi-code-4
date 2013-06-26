"""Models for the ``cmsplugin_blog_seo_addons`` app."""
from django.db import models
from django.utils.translation import ugettext_lazy as _, get_language

from cmsplugin_blog.models import Entry
from django_libs.models_mixins import SimpleTranslationMixin
from simple_translation.utils import get_preferred_translation_from_lang


class SEOAddon(SimpleTranslationMixin, models.Model):
    """An SEO meta data addon for an cmsplugin_blog ``Entry``."""

    def __unicode__(self):
        return self.get_translation().meta_description[:50]

    def get_meta_description(self):
        lang = get_language()
        return get_preferred_translation_from_lang(
            self, lang).get_meta_description()


class EntrySEOAddon(models.Model):
    """
    An intermediary model to attach seo addons to an ``Entry`` object.

    :entry: The ``Entry`` instance the ``SEOAddon`` should be attached to.
    :seoaddon: The ``SEOAddon`` instance that is attached to the ``Entry``.

    """
    entry = models.ForeignKey(
        Entry,
        verbose_name=_('Entry'),
    )

    seoaddon = models.ForeignKey(
        SEOAddon,
        verbose_name=_('SEO addon'),
        blank=True, null=True,
    )


class SEOAddonTranslation(models.Model):
    """
    The translatable fields of the ``EntrySEOAddon``

    :meta_description: The meta description to insert on the page.

    """
    meta_description = models.TextField(
        max_length=512,
        verbose_name=_('Meta description'),
        blank=True,
    )

    # needed by simple_translation
    seoaddon = models.ForeignKey(
        SEOAddon,
        verbose_name=_('SEO addon'),
    )

    language = models.CharField(
        max_length=5,
        verbose_name=('Language'),
    )

    def get_meta_description(self):
        if self.meta_description:
            if len(self.meta_description) > 160:
                return '{}...'.format(self.meta_description[:160])
            return self.meta_description
