# -*- coding: utf-8 -*-
"""Test misc functions in misc.py file."""

from plone.hud.misc import normalize_name
from plone.hud.misc import get_panel_id

import unittest2


class TestMisc(unittest2.TestCase):

    def test_normalize_name(self):
        self.assertEqual(
            normalize_name("Users Panel"),
            "users_panel"
        )
        self.assertEqual(
            normalize_name("Users_Panel"),
            "users_panel"
        )

    def test_get_panel_id(self):
        self.assertEqual(
            get_panel_id("Users Panel"),
            "hud_users_panel"
        )
        self.assertEqual(
            get_panel_id("Users_Panel"),
            "hud_users_panel"
        )
