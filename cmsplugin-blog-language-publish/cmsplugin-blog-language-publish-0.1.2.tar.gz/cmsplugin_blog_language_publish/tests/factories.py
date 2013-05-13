"""Factories for the models of the ``cmsplugin_blog_language_publish`` app."""
import factory

from cmsplugin_blog.models import Entry, EntryTitle

from ..models import EntryLanguagePublish


class EntryFactory(factory.Factory):
    """Factory for the ``Entry`` model from ``cmsplugin_blog``."""
    FACTORY_FOR = Entry

    is_published = True


class EntryTitleFactory(factory.Factory):
    """Factory for the ``EntryTitle`` model from ``cmsplugin_blog``."""
    FACTORY_FOR = EntryTitle

    entry = factory.SubFactory(EntryFactory)
    title = 'Foobar'
    slug = 'foobar'


class EntryLanguagePublishFactory(factory.Factory):
    """Factory for the ``EntryLanguagePublish`` model."""
    FACTORY_FOR = EntryLanguagePublish

    entry_title = factory.SubFactory(EntryTitleFactory)
