# -*- coding: utf-8 -*-
"""
Django TailorDev CMS

Test commands.
"""
from django.test import TestCase

from ..management.commands import cms_lorem_fixtures
from ..models import Category, Page


class CMSLoremFixturesCommandTests(TestCase):
    """
    Tests for the cms_lorem_fixtures command
    """
    def test_command(self):
        """
        Test that the command creates pages and categories
        """
        cmd = cms_lorem_fixtures.Command()
        cmd.handle()

        self.assertEqual(Category.objects.count(), 9)
        self.assertEqual(Page.objects.count(), 18)
