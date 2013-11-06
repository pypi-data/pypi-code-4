from Products.CMFCore.utils import getToolByName
from collective.cart.core.tests.base import IntegrationTestCase

import mock


class TestCase(IntegrationTestCase):
    """TestCase for upgrade steps"""

    def get_action(self, category, name):
        """Get action by category and name."""
        actions = getToolByName(self.portal, 'portal_actions')
        return getattr(getattr(actions, category), name)

    def test_reimport_actions(self):
        action = self.get_action('object', 'orders')
        action.visible = False
        self.assertFalse(action.visible)

        from collective.cart.core.upgrades import reimport_actions
        reimport_actions(self.portal)

        self.assertTrue(action.visible)

    @mock.patch('collective.cart.core.upgrades.getToolByName')
    def test_reimport_rolemap(self, getToolByName):
        from collective.cart.core.upgrades import reimport_rolemap
        reimport_rolemap(self.portal)
        getToolByName().runImportStepFromProfile.assert_called_with(
            'profile-collective.cart.core:default', 'rolemap', run_dependencies=False, purge_old=False)

    @mock.patch('collective.cart.core.upgrades.getToolByName')
    def test_reimport_typeinfo(self, getToolByName):
        from collective.cart.core.upgrades import reimport_typeinfo
        reimport_typeinfo(self.portal)
        getToolByName().runImportStepFromProfile.assert_called_with(
            'profile-collective.cart.core:default', 'typeinfo', run_dependencies=False, purge_old=False)

    def test_reimport_workflows(self):
        workflow = getToolByName(self.portal, 'portal_workflow')
        workflow.setChainForPortalTypes(('collective.cart.core.Order', ), '')
        self.assertEqual(workflow.getChainForPortalType('collective.cart.core.Order'), ())

        from collective.cart.core.upgrades import reimport_workflows
        reimport_workflows(self.portal)

        self.assertEqual(workflow.getChainForPortalType('collective.cart.core.Order'), ('order_default_workflow',))
