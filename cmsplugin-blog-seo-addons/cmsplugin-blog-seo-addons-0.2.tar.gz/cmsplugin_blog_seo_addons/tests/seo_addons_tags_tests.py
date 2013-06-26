"""Tests for the template tags of the ``cmsplugin_blog_seo_addons`` app."""
from django.test import TestCase
from django.test.client import RequestFactory

from cms.models.placeholdermodel import Placeholder
from cms.plugins.text.models import Text
from cms.plugins.picture.models import Picture
from cms.plugins.link.models import Link

from ..templatetags.seo_addons_tags import get_entry_meta_description
from .factories import EntrySEOAddonFactory


class GetEntryMetaDescriptionTestCase(TestCase):
    """Tests for the ``get_entry_meta_description`` template tag."""
    longMessage = True

    def setUp(self):
        self.entryaddon = EntrySEOAddonFactory()
        self.entry = self.entryaddon.entry
        self.placeholder = Placeholder.objects.create(slot='excerpt')
        self.sample_text = (
            'An extra long string, that is much longer than 160 so it gets'
            ' cut off properly in an attempt to raise the test coverage'
            ' to one hundret percent. Should have used a lorem ipsum'
            ' generator for it.')
        self.text = Text.objects.create(
            placeholder=self.placeholder,
            language='en',
            plugin_type='TextPlugin',
            body='<span>{}</span>'.format(self.sample_text),
        )
        self.link = Link.objects.create(
            placeholder=self.placeholder,
            language='en',
            plugin_type='TextPlugin',
            name='link name',
            url='https://www.exampe.com/',
        )
        self.picture = Picture.objects.create(
            placeholder=self.placeholder,
            language='en',
            plugin_type='TextPlugin',
        )
        self.entry.placeholders.add(self.placeholder)
        self.req = RequestFactory().get('/')
        self.req.LANGUAGE_CODE = 'en'

    def test_tag(self):
        # Test if the meta description is fetched from the seo addon
        self.assertEqual(get_entry_meta_description(self.entry, self.req),
                         self.entryaddon.seoaddon.get_meta_description())

        # Test if it outputs the content from the text plugin
        self.entryaddon.delete()
        self.assertIn(get_entry_meta_description(self.entry, self.req)[:-3],
                      self.sample_text,
                      msg=('The description was not the one from the text'
                           ' plugin.'))
        self.text.body = 'foobar'
        self.text.save()
        self.assertEqual(get_entry_meta_description(self.entry, self.req),
                         'foobar',
                         msg=('The description was not the one from the text'
                              ' plugin.'))
