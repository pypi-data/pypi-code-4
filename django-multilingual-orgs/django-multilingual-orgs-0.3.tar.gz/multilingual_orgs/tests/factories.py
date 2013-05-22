"""Factories for the ``multilingual_orgs`` app."""
import factory

from django_libs.tests.factories import SimpleTranslationMixin
from people.tests.factories import PersonFactory

from ..models import (
    Organization,
    OrganizationPluginModel,
    OrganizationPersonRole,
    OrganizationTranslation,
)


class OrganizationBaseFactory(factory.Factory):
    """
    Factory for the ``Organization`` model to use in the
    ``OrganizationTranslationFactory``.

    Without the ``SimpleTranslationMixin``, because it creates extra
    ``OrganizationTranslation`` objects in the tests.

    """
    FACTORY_FOR = Organization


class OrganizationFactory(SimpleTranslationMixin, factory.Factory):
    """Factory for the ``Organization`` model."""
    FACTORY_FOR = Organization

    @staticmethod
    def _get_translation_factory_and_field():
        return (OrganizationTranslationFactory, 'organization')


class OrganizationPersonRoleFactory(factory.Factory):
    """Factory for the ``OrganizationPersonRole`` model."""
    FACTORY_FOR = OrganizationPersonRole

    organization = factory.SubFactory(OrganizationFactory)
    person = factory.SubFactory(PersonFactory)


class OrganizationPluginModelFactory(factory.Factory):
    """Factory for ``OrganizationPluginModel`` objects."""
    FACTORY_FOR = OrganizationPluginModel

    display_type = 'small'
    organization = factory.SubFactory(OrganizationFactory)


class OrganizationTranslationFactory(factory.Factory):
    """Factory for ``OrganizationTranslation`` objects."""
    FACTORY_FOR = OrganizationTranslation

    title = factory.Sequence(lambda n: 'my org title {0}'.format(n))
    organization = factory.SubFactory(OrganizationBaseFactory)
    language = 'en'
