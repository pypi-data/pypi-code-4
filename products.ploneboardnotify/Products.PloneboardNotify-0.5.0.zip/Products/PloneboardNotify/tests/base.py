"""Test setup for integration and functional tests.

When we import PloneTestCase and then call setupPloneSite(), all of
Plone's products are loaded, and a Plone site will be created. This
happens at module level, which makes it faster to run each test, but
slows down test runner startup.
"""

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

# When ZopeTestCase configures Zope, it will *not* auto-load products
# in Products/. Instead, we have to use a statement such as:
#   ztc.installProduct('SimpleAttachment')
# This does *not* apply to products in eggs and Python packages (i.e.
# not in the Products.*) namespace. For that, see below.
# All of Plone's products are already set up by PloneTestCase.

@onsetup
def setup_product():
    """Set up the package and its dependencies.

    The @onsetup decorator causes the execution of this body to be
    deferred until the setup of the Plone site testing layer. We could
    have created our own layer, but this is the easiest way for Plone
    integration tests.
    """

    # Load the ZCML configuration for the example.tests package.
    # This can of course use <include /> to include other packages.

    fiveconfigure.debug_mode = True
    import Products.Ploneboard
    import Products.PloneboardNotify
    zcml.load_config('configure.zcml', Products.Ploneboard)
    zcml.load_config('configure.zcml', Products.PloneboardNotify)
    fiveconfigure.debug_mode = False


ztc.installProduct('Ploneboard')
ztc.installProduct('PloneboardNotify')

# The order here is important: We first call the (deferred) function
# which installs the products we need for this product. Then, we let
# PloneTestCase set up this product on installation.

setup_product()
# Below I don't use Products.xxx for Plone 2.5 compatibility
ptc.setupPloneSite(products=['Products.CMFPlacefulWorkflow',
                             'Products.PloneboardNotify'])

class TestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If
    necessary, we can put common utility or setup code in here. This
    applies to unit test cases.
    """

class FunctionalTestCase(ptc.FunctionalTestCase):
    """We use this class for functional integration tests that use
    doctest syntax. Again, we can put basic common utility or setup
    code in here.
    """

    def afterSetUp(self):
        self.portal.portal_membership.addMember('root', 'secret',
                                                ('Manager','Owner'), [],
                                                properties={'fullname': 'The Admin',
                                                            'email': 'admin@mysite.org'})
        self.portal.portal_membership.addMember('member', 'secret',
                                                ('Member',), [],
                                                properties={'fullname': 'The Member',
                                                            'email': 'user@mysite.org'})
        self.portal.portal_membership.addMember('another_member', 'secret',
                                                ('Member',), [],
                                                properties={'fullname': 'Another Member',
                                                            'email': 'another@mysite.org'})

    def enableForumGlobally(self):
        portal_types = self.portal.portal_types
        forum_type = portal_types.getTypeInfo('PloneboardForum')
        forum_type.global_allow = True

