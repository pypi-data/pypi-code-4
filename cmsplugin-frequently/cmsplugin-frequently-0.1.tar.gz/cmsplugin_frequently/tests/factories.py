"""
Factories for the ``cmsplugin_frequently`` app.

"""
import factory

from cmsplugin_frequently import models


class FrequentlyEntryCategoryPluginFactory(factory.Factory):
    """
    Factory for factories for ``FrequentlyEntryCategoryPlugin`` models.

    """
    FACTORY_FOR = models.FrequentlyEntryCategoryPlugin
