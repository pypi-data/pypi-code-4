from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.testing import z2

import collective.request.player


COLLECTIVE_REQUEST_PLAYER = PloneWithPackageLayer(
    zcml_package=collective.request.player,
    zcml_filename='testing.zcml',
    gs_profile_id='collective.request.player:testing',
    name="COLLECTIVE_REQUEST_PLAYER")

COLLECTIVE_REQUEST_PLAYER_INTEGRATION = IntegrationTesting(
    bases=(COLLECTIVE_REQUEST_PLAYER, ),
    name="COLLECTIVE_REQUEST_PLAYER_INTEGRATION")

COLLECTIVE_REQUEST_PLAYER_FUNCTIONAL = FunctionalTesting(
    bases=(COLLECTIVE_REQUEST_PLAYER, z2.ZSERVER_FIXTURE),
    name="COLLECTIVE_REQUEST_PLAYER_FUNCTIONAL")
