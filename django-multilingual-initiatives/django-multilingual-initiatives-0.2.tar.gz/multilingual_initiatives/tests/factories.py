"""Factories for the ``multilingual_initiatives`` app."""
import factory

from django_libs.tests.factories import SimpleTranslationMixin
from people.tests.factories import PersonFactory

from ..models import (
    Initiative,
    InitiativePersonRole,
    InitiativePluginModel,
    InitiativeTranslation,
)


class InitiativeBaseFactory(factory.Factory):
    """
    Factory for the ``Initiative`` model to use in the
    ``InitiativeTranslationFactory``.

    Without the ``SimpleTranslationMixin``, because it creates extra
    ``InitiativeTranslation`` objects in the tests.

    """
    FACTORY_FOR = Initiative


class InitiativeFactory(SimpleTranslationMixin, factory.Factory):
    """Factory for the ``Initiative`` model."""
    FACTORY_FOR = Initiative

    @staticmethod
    def _get_translation_factory_and_field():
        return (InitiativeTranslationFactory, 'initiative')


class InitiativePersonRoleFactory(factory.Factory):
    """Factory for the ``InitiativePersonRole`` model."""
    FACTORY_FOR = InitiativePersonRole

    initiative = factory.SubFactory(InitiativeFactory)
    person = factory.SubFactory(PersonFactory)


class InitiativePluginModelFactory(factory.Factory):
    """Factory for ``InitiativePluginModel`` objects."""
    FACTORY_FOR = InitiativePluginModel

    display_type = 'small'
    initiative = factory.SubFactory(InitiativeFactory)


class InitiativeTranslationFactory(factory.Factory):
    """Factory for ``InitiativeTranslation`` objects."""
    FACTORY_FOR = InitiativeTranslation

    title = factory.Sequence(lambda n: 'my initiative title {0}'.format(n))
    initiative = factory.SubFactory(InitiativeBaseFactory)
    language = 'en'
