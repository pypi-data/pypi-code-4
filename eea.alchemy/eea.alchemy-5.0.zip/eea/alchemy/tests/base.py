""" Base test cases
"""
from Products.Five import zcml
from Products.Five import fiveconfigure
from eea.alchemy.controlpanel.interfaces import IAlchemySettings
from eea.alchemy.tests.fake import FakeAlchemyAPI, IAlchemyAPI
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from zope.component import provideUtility
import eea.alchemy
import logging

logger = logging.getLogger('eea.alchemy.tests.base')

@onsetup
def setup_eea_alchemy():
    """ Set up the additional products.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', eea.alchemy)
    fiveconfigure.debug_mode = False

    provideUtility(FakeAlchemyAPI(), IAlchemyAPI)

setup_eea_alchemy()
ptc.setupPloneSite(extension_profiles=('eea.alchemy:default',))

class EEAAlchemyTestCase(ptc.PloneTestCase):
    """ Base class for integration tests for the 'EEA Alchemy' product.
    """

class EEAAlchemyFunctionalTestCase(ptc.FunctionalTestCase, EEAAlchemyTestCase):
    """ Base class for functional integration tests for
        the 'EEA Alchemy' product.
    """
    _sandbox = None
    _brain = None

    @property
    def sandbox(self):
        """ Sandbox
        """
        return self._sandbox

    @property
    def brain(self):
        """ Brain
        """
        return self._brain

    def afterSetUp(self):
        """ Setup
        """
        sid = self.folder.invokeFactory('Folder', id='sandbox')
        sandbox = self.folder._getOb(sid)
        sandbox.processForm(data=1, metadata=1, values={
            'title': (
                "Formation of new land cover in the region of Valencia, Spain"
            ),
            'description': (
                "Urban sprawl 1990-2000 in the province of Venice "
                "using a 1 km x 1 km grid"
            ),
        })
        self._sandbox = sandbox

        sid = sandbox.getId()
        brains = self.portal.portal_catalog(getId=sid)
        self._brain = brains[0]

        atool = IAlchemySettings(self.portal)
        atool.token = u'12345665766867'
