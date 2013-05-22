"""Tests for the models of the ``multilingual_initiatives`` app."""
from mock import Mock

from django.test import TestCase

from ..models import Initiative
from .factories import (
    InitiativeFactory,
    InitiativePersonRoleFactory,
    InitiativePluginModelFactory,
    InitiativeTranslationFactory,
)


class InitiativeManagerTestCase(TestCase):
    """Tests for the ``InitiativeManager`` model manager."""
    longMessage = True

    def setUp(self):
        self.en_ini = InitiativeTranslationFactory(language='en')
        self.de_ini = InitiativeTranslationFactory(language='de')
        InitiativeTranslationFactory(language='de', is_published=True,
                                     initiative=self.de_ini.initiative)
        InitiativeTranslationFactory(language='en', is_published=True,
                                     initiative=self.en_ini.initiative)

    def test_manager(self):
        """Test, if the ``InitiativeManager`` returns the right entries."""
        request = Mock(LANGUAGE_CODE='de')
        self.assertEqual(
            Initiative.objects.published(request).count(), 1, msg=(
                'In German, there should be two published initiatives.'))

        request = Mock(LANGUAGE_CODE='en')
        self.assertEqual(
            Initiative.objects.published(request).count(), 1, msg=(
                'In English, there should be one published initiative.'))

        request = Mock(LANGUAGE_CODE=None)
        self.assertEqual(
            Initiative.objects.published(request).count(), 0, msg=(
                'If no language set, there should be no published'
                ' initiatives.'))


class InitiativeTestCase(TestCase):
    """Tests for the ``Initiative`` model."""
    longMessage = True

    def test_model(self):
        obj = InitiativeFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to instantiate and save the model.'))
        self.assertTrue(obj.get_translation(), msg=(
            'The factory should also create a translation'))


class InitiativePersonRoleTestCase(TestCase):
    """Tests for the ``InitiativePersonRole`` model."""
    longMessage = True

    def test_model(self):
        obj = InitiativePersonRoleFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to instantiate and save the model.'))


class InitiativePluginModelTestCase(TestCase):
    """Tests for the ``InitiativePluginModel`` model."""
    longMessage = True

    def test_model(self):
        obj = InitiativePluginModelFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to instantiate and save the model.'))


class InitiativeTranslationTestCase(TestCase):
    """Tests for the ``InitiativeTranslation`` model."""
    longMessage = True

    def test_model(self):
        """Test instantiation of the ``InitiativeTranslation`` model."""
        obj = InitiativeTranslationFactory(title='my initiative')
        self.assertTrue(obj.pk, msg=(
            'Should be able to instantiate and save the model.'))
