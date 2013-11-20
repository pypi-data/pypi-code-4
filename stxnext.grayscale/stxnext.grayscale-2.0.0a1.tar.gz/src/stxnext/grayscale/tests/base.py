
# -*- coding: utf-8 -*-
"""Base module for unittesting."""

import unittest

from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import quickInstallProduct


class GrayscaleLayer(PloneSandboxLayer):
    """Testing layer for stxnext.grayscale addon"""

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        import stxnext.grayscale

        self.loadZCML(package=stxnext.grayscale)

        from OFS.Application import install_package
        install_package(app, stxnext.grayscale, stxnext.grayscale.initialize)

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # install stxnext.grayscale
        quickInstallProduct(portal, 'stxnext.grayscale')

        import transaction
        transaction.commit()

    def tearDownZope(self, app):
        """Tear down Zope."""
        pass


FIXTURE = GrayscaleLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="GrayscaleLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="GrayscaleLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING

class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING

