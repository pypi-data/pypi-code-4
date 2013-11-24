"""Just an empty models file to let the testrunner recognize this as app."""
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin
from frequently.models import EntryCategory


class FrequentlyEntryCategoryPlugin(CMSPlugin):
    """
    CMS related Model to get a group of desired categories.

    :categories: Categories, which are selected by the cms user.

    """
    categories = models.ManyToManyField(
        EntryCategory,
        verbose_name=_('Categories'),
        related_name='cmsplugin_frequently_entrycategoryplugins'
    )

    def copy_relations(self, oldinstance):
        self.categories = oldinstance.categories.all()
