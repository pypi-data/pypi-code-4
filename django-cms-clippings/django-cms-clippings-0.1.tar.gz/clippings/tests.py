import mock

from django.conf import settings
from django.contrib.sites.models import Site
from django.core import mail
from django.db.utils import IntegrityError
from django.test import TestCase
from django.test.client import RequestFactory
from django.template import Template, Context
from django.utils.translation import get_language

from cms.api import add_plugin

from clippings.models import Clipping


class ShowClippingTemplateTagTestCase(TestCase):
    """Tests for the show_clipping template tag."""

    def setUp(self):
        self.content = "hello, world"

        clipping = Clipping.objects.create(
            site=Site.objects.all()[0], identifier="clipping")

        add_plugin(clipping.content, "TextPlugin", get_language(),
                   body=self.content)

        self.template = Template(
            '{% load clippings_tags %}{% show_clipping "clipping" %}')
        self.context = Context({'request': RequestFactory().get('/')})

    def test_render_clipping(self):
        """Verify the template tag is replaced with the clipping content."""
        self.assertEqual(self.content, self.template.render(self.context))

    def test_render_missing_clipping(self):
        """Verify the template is rendered if the clipping does not exist."""
        Clipping.objects.all().delete()
        self.assertEqual("", self.template.render(self.context))

    def test_missing_clipping_raises_exception(self):
        """Verify an exception is raised if the clipping does not exist."""
        Clipping.objects.all().delete()

        with mock.patch.object(settings, 'REPORT_MISSING_CLIPPING', True):
            with mock.patch.object(settings, 'DEBUG', True):
                self.assertRaises(Clipping.DoesNotExist, self.template.render,
                                  self.context)

    def test_missing_clipping_sends_email(self):
        """Verify an email is sent if the clipping does not exist."""
        Clipping.objects.all().delete()

        with mock.patch.object(settings, 'REPORT_MISSING_CLIPPING', True):
            with mock.patch.object(settings, 'SEND_BROKEN_LINK_EMAILS', True):
                with mock.patch.object(settings, 'DEBUG', False):
                    self.template.render(self.context)
                    result = mail.outbox[0].subject
                    self.assertTrue('Clipping not found' in result)

    def test_duplicate_clippings_raises_exception(self):
        """Verify Clippings are unique for a given site."""
        self.assertRaises(IntegrityError, Clipping.objects.create,
                          site=Site.objects.all()[0], identifier="clipping")
