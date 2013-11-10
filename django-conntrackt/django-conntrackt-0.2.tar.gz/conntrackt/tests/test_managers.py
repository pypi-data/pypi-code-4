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


# Python third-party library imports.
import mock

# Django imports.
from django.test import TestCase
from django.db import models

# Application imports.
from conntrackt.models import SearchManager, Project


class SearchManagerTest(TestCase):

    @mock.patch("conntrackt.models.Q")
    def test_search(self, q_object):
        """
        Test the search method of custom manager.
        """

        # Create a dummy model that uses the custom manager.
        class TestModel(models.Model):
            objects = SearchManager()

        # Mock the filter call so we can check what it got called with.
        TestModel.objects.filter = mock.MagicMock()

        # Set-up an instance of mocked Q object that we'll use for validating
        # the call.
        q_instance = mock.Mock()

        # Mock the __or__ call.
        q_or_method = mock.Mock()
        q_or_method.return_value = q_instance
        q_instance.__or__ = q_or_method

        # Finaly, when the constructor is called, we should return our own
        # instance.
        q_object.return_value = q_instance

        # Call the search.
        results = TestModel.objects.search("test")

        # Check if we had bee called with our mocked Q instance.
        TestModel.objects.filter.assert_has_calls([mock.call(q_instance)])
        TestModel.objects.filter.assert_called_with(q_instance)
        q_instance.__or__.assert_called_with(q_instance)
