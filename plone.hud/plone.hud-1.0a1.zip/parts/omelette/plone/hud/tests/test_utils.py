# -*- coding: utf-8 -*-
"""Test utilities, helper functions."""

from plone.hud import register_hud_panel
from plone.hud import unregister_hud_panel
from plone.hud.testing import IntegrationTestCase


class TestUtils(IntegrationTestCase):

    def test_register_panel_cycle(self):
        panel_name = "Sheeps"

        panel_id = register_hud_panel(panel_name)

        self.assertEqual(panel_id, "hud_sheeps")

        panel_id = unregister_hud_panel(panel_name)

        self.assertEqual(panel_id, "hud_sheeps")
