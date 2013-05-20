"""Tests for the models of the ``multilingual_orgs`` app."""
from mock import Mock

from django.test import TestCase

from ..models import Organization
from .factories import (
    OrganizationFactory,
    OrganizationPluginModelFactory,
    OrganizationTranslationFactory,
)


class OrganizationManagerTestCase(TestCase):
    """Tests for the ``OrganizationManager`` model manager."""
    longMessage = True

    def setUp(self):
        self.en_org = OrganizationTranslationFactory(language='en')
        self.de_org = OrganizationTranslationFactory(language='de')
        OrganizationTranslationFactory(language='de', is_published=True,
                                       organization=self.de_org.organization)
        OrganizationTranslationFactory(language='en', is_published=True,
                                       organization=self.en_org.organization)

    def test_manager(self):
        """Test, if the ``OrganizationManager`` returns the right entries."""
        request = Mock(LANGUAGE_CODE='de')
        self.assertEqual(
            Organization.objects.published(request).count(), 1, msg=(
                'In German, there should be two published organizations.'))

        request = Mock(LANGUAGE_CODE='en')
        self.assertEqual(
            Organization.objects.published(request).count(), 1, msg=(
                'In English, there should be one published organization.'))

        request = Mock(LANGUAGE_CODE=None)
        self.assertEqual(
            Organization.objects.published(request).count(), 0, msg=(
                'If no language set, there should be no published'
                ' organizations.'))


class OrganizationTestCase(TestCase):
    """Tests for the ``Organization`` model."""
    longMessage = True

    def test_model(self):
        obj = OrganizationFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to instantiate and save the model.'))
        self.assertTrue(obj.get_translation(), msg=(
            'The factory should also create a translation'))


class OrganizationPluginModelTestCase(TestCase):
    """Tests for the ``OrganizationPluginModel`` model."""
    longMessage = True

    def test_model(self):
        obj = OrganizationPluginModelFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to instantiate and save the model.'))


class OrganizationTranslationTestCase(TestCase):
    """Tests for the ``OrganizationTranslation`` model."""
    longMessage = True

    def test_model(self):
        """Test instantiation of the ``OrganizationTranslation`` model."""
        obj = OrganizationTranslationFactory(title='my org')
        self.assertTrue(obj.pk, msg=(
            'Should be able to instantiate and save the model.'))
