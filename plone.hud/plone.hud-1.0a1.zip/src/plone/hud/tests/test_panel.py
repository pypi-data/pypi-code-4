# -*- coding: utf-8 -*-
"""Tests panel view related functions."""

from plone.hud import register_hud_panel
from plone.hud.testing import IntegrationTestCase

import mock


class TestPanel(IntegrationTestCase):
    """Integration tests for panel."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.panel = self.portal.unrestrictedTraverse("@@hud")

    def prepare_panel_env(self, request_form={}):
        """Prepare all the variables for various tests.

        Also, optionally you can set 'request_form' (it must be dict type),
        this updates the values in the view.request.form,
        it does not remove any keys.
        """
        # we do not render any templates inside integration tests
        with mock.patch(
            'plone.hud.panel.'
            'HUDPanelView.main_template'
        ):
            self.panel.request.form.update(request_form)
            self.panel.render()

    def test_get_panels(self):
        # register panels
        register_hud_panel("Sheeps")
        register_hud_panel("Goats")
        register_hud_panel("Cats")
        register_hud_panel("Dogs")

        # prepare environment
        self.prepare_panel_env()

        # mock restricted traverse and return mocked title
        self.panel.portal.restrictedTraverse = mock.Mock()
        self.panel.portal.restrictedTraverse.return_value.title = \
            "Mocked Title"

        # test the results
        self.assertEqual(
            self.panel.get_panels(),
            [
                {
                    'url': 'http://nohost/plone/@@hud?panel_name=hud_cats',
                    'name': 'hud_cats', 'title': 'Mocked Title'
                }, {
                    'url': 'http://nohost/plone/@@hud?panel_name=hud_dogs',
                    'name': 'hud_dogs', 'title': 'Mocked Title'
                }, {
                    'url': 'http://nohost/plone/@@hud?panel_name=hud_goats',
                    'name': 'hud_goats', 'title': 'Mocked Title'
                }, {
                    'url': 'http://nohost/plone/@@hud?panel_name=hud_sheeps',
                    'name': 'hud_sheeps', 'title': 'Mocked Title'
                }
            ]
        )
