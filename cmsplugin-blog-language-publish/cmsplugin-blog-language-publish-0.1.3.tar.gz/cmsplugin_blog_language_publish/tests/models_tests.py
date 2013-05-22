"""Tests for the models of the ``cmsplugin_blog_language_publish`` app."""
from django.test import TestCase

from .factories import EntryLanguagePublishFactory


class EntryLanguagePublishTestCase(TestCase):
    """Tests for the ``EntryLanguagePublish`` model class."""
    longMessage = True

    def test_instantiation(self):
        """
        Test instantiation and save of the ``EntryLanguagePublish`` model.

        """
        instance = EntryLanguagePublishFactory()
        self.assertTrue(instance.pk, msg=(
            'There should be one EntryLanguagePublish object.'))
