# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Branko Majic
#
# This file is part of Django Conntrackt.
#
# Django Conntrackt is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Django Conntrackt is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Django Conntrackt.  If not, see <http://www.gnu.org/licenses/>.
#


# Django imports.
from django.test import TestCase

# Python third-party library imports.
import mock

# Application imports.
from conntrackt.forms import WidgetCSSClassFormMixin, PlaceholderFormMixin
from conntrackt.forms import EntityForm, InterfaceForm, CommunicationForm

# Test imports.
from .forms import FormWithWidgetCSSClassFormMixin, FormWithPlaceholderFormMixin


class WidgetCSSClassFormMixinTest(TestCase):
    """
    Tests the form mixin.
    """

    def test_apply_to_all(self):
        """
        Test if CSS class is appled to all form field widgets.
        """

        # Set-up the form.
        form_class = FormWithWidgetCSSClassFormMixin
        form_class.widget_css_classes = {"ALL": "test"}
        form = form_class()

        self.assertEqual(form.fields["field1"].widget.attrs["class"], "test")
        self.assertEqual(form.fields["field2"].widget.attrs["class"], "test")

    def test_apply_to_single(self):
        """
        Test if CSS class is appled to a single field widget.
        """

        # Set-up the form.
        form_class = FormWithWidgetCSSClassFormMixin
        form_class.widget_css_classes = {"field2": "test"}
        form = form_class()

        self.assertEqual(form.fields["field1"].widget.attrs.get("class", None), None)
        self.assertEqual(form.fields["field2"].widget.attrs["class"], "test")

    def test_apply_multiple(self):
        """
        Tests if different class is applied to multiple form field widgets.
        """

        # Set-up the form.
        form_class = FormWithWidgetCSSClassFormMixin
        form_class.widget_css_classes = {"field1": "f1",
                                         "field2": "f2"}
        form = form_class()

        self.assertEqual(form.fields["field1"].widget.attrs["class"], "f1")
        self.assertEqual(form.fields["field2"].widget.attrs["class"], "f2")

    def test_apply_to_all_additional(self):
        """
        Tests if all widgets get the same CSS class in addition to induvidual
        ones.
        """

        # Set-up the form.
        form_class = FormWithWidgetCSSClassFormMixin
        form_class.widget_css_classes = {"field1": "f1",
                                         "field2": "f2",
                                         "ALL": "all"}
        form = form_class()

        self.assertEqual(sorted(["f1", "all"]), sorted(form.fields["field1"].widget.attrs["class"].split(" ")))
        self.assertEqual(sorted(["f2", "all"]), sorted(form.fields["field2"].widget.attrs["class"].split(" ")))


class PlaceholderFormMixinTest(TestCase):
    """
    Tests the form mixin.
    """

    def test_apply_one(self):
        """
        Test if a single placeholder is applied to a form field widget.
        """

        # Set-up the form.
        form_class = FormWithPlaceholderFormMixin
        form_class.widget_placeholders = {"field1": "place1"}
        form = form_class()

        self.assertEqual(form.fields["field1"].widget.attrs["placeholder"], "place1")
        self.assertEqual(form.fields["field2"].widget.attrs.get("placeholder", None), None)

    def test_apply_multiple(self):
        """
        Test if multiple placeholders are applied to form field widgets.
        """

        # Set-up the form.
        form_class = FormWithPlaceholderFormMixin
        form_class.widget_placeholders = {"field1": "place1",
                                   "field2": "place2"}
        form = form_class()

        self.assertEqual(form.fields["field1"].widget.attrs["placeholder"], "place1")
        self.assertEqual(form.fields["field2"].widget.attrs["placeholder"], "place2")
