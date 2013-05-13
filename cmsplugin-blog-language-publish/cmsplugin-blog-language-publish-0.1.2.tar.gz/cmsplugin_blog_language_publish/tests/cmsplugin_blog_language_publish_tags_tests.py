"""Tests for the ``cmsplugin_blog_language_publish`` app's template tags."""
from django.test import TestCase

from cmsplugin_blog.models import Entry

from ..templatetags.cmsplugin_blog_language_publish_tags import (
    get_published_entries)
from .factories import EntryLanguagePublishFactory


class GetPublishedEntryTestCase(TestCase):
    """Test for the ``get_published_entry`` template tag."""
    longMessage = True

    def setUp(self):
        self.entry_langpub = EntryLanguagePublishFactory(published=True)
        self.entry_not_published = EntryLanguagePublishFactory()

    def test_template_tag(self):
        """Test for the ``get_published_entry`` template tag."""
        entries = Entry.objects.all()
        entries = get_published_entries(entries, 'en')
        self.assertEqual(len(entries), 1, msg=(
            'Should return the entries that are published.'))
