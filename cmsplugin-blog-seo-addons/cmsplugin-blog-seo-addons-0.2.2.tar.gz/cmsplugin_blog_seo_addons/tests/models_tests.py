"""Tests for the models of the ``cmsplugin_blog_seo_addons`` app."""
from django.test import TestCase

from .factories import BaseSEOAddonFactory, SEOAddonTranslationFactory


class SEOAddonTestCase(TestCase):
    """Tests for the ``SEOAddon`` model class."""
    longMessage = True

    def test_instantiation_and_get_description(self):
        """Test instantiation of the ``SEOAddon`` model."""
        seoaddon = BaseSEOAddonFactory()
        self.assertTrue(seoaddon.pk)


class SEOAddonTranslationTestCase(TestCase):
    """Tests for the ``SEOAddonTranslation`` model class."""
    longMessage = True

    def test_instantiation_and_get_description(self):
        """
        Test instantiation and get_meta_description of the
        ``SEOAddonTranslation`` model.

        """
        seoaddontranslation = SEOAddonTranslationFactory(
            meta_description=(
                'An extra long string, that is much longer than 160 so it gets'
                ' cut off properly in an attempt to raise the test coverage'
                ' to one hundret percent. Should have used a lorem ipsum'
                ' generator for it.'))
        self.assertTrue(seoaddontranslation.pk)

        self.assertIn(seoaddontranslation.seoaddon.get_meta_description()[:-3],
                      seoaddontranslation.meta_description)
