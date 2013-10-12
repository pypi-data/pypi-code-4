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


# Python standard library imports.
from types import FunctionType

# Python third-party library imports.
import mock

# Django imports.
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User, Permission
from django.test import RequestFactory


def create_get_request(url="/fake-path/", user=None):
    """
    Helper function for generating a GET request that can be passed on to a
    view.

    Arguments:

        url - URL that should be used for the request. Default is "/fake-path/".

        user - Django user to be passed on into the request. Default is
        mock.Mock().
    """

    request = RequestFactory().get(url)

    # If user was not provided, construct one using mocking.
    if user is None:
        user = mock.Mock()

    request.user = user

    return request


def generate_get_response(view, request=None, *args, **kwargs):
    """
    Generates a get response, passing the request, positional and keyword
    arguments to it as well.

    Attributes:

        view - View function that should be called.

        request - Request object to pass into view. Default is to create a new
        request using the create_get_request() call.

        *args - Additional positional arguments that will be passed into view.

        *kwargs - Additional keyword arguments that will be passed into view.
    """

    # If no request was provided, construct it.
    if request is None:
        request = create_get_request()

    return view(request, *args, **kwargs)


class PermissionTestMixin(object):
    """
    Mixin class for testing if permission requirement is applied properly for
    accessing a view.

    In order to use this mixin, add it the left side of the class list the test
    is inheriting from, and configure it providing the following class options:

        view_class - Class used for the CBV that will be tested.
        view_function - View function that will be tested.
        sufficient_permissions - Permissions sufficient to gain access to view.
        permission_test_view_args - Positional arguments to pass to the view.
        permission_test_view_kwargs - Keyword arguments to pass to the view.
    """

    view_class = None
    view_function = None
    permission_test_view_args = ()
    permission_test_view_kwargs = {}
    sufficient_permissions = ()

    def __init__(self, *args, **kwargs):
        """
        Initialises the mixin. Takes care of some basic validation of passed
        configuration options.
        """

        super(PermissionTestMixin, self).__init__(*args, **kwargs)

        if self.view_class is None and self.view_function is None:
            raise ValueError("Permission test mixin configured improperly - no CBV class or function was supplied via parameters 'view_class' or 'view_function'.")

        if self.view_function is not None and type(self.view_function) is not FunctionType:
            raise ValueError("Permission test mixin configured improperly - provided 'view_function' is not function. Did you forget to wrap the function with staticmethod() perhaps?")

        if type(self.permission_test_view_kwargs) is not dict:
            raise ValueError("Permission text mixin configured improperly - parameter 'permission_test_view_kwargs' must be a dictionary.")

        if type(self.permission_test_view_args) is not tuple:
            raise ValueError("Permission text mixin configured improperly - parameter 'permission_test_view_args' must be a tuple.")

        if type(self.sufficient_permissions) is not tuple:
            raise ValueError("Permission text mixin configured improperly - parameter 'sufficient_permissions' must be a tuple.")

    def test_permission_granted(self):
        # Set-up a request from user with sufficient privileges.
        request = RequestFactory().get("/fake-path")
        user = User.objects.create(username="user", password="password")
        for permission in self.sufficient_permissions:
            user.user_permissions.add(Permission.objects.get(codename=permission))
        request.user = user

        # Get the view.
        if self.view_class is not None:
            view = self.view_class.as_view()
        elif self.view_function is not None:
            view = self.view_function

        # Verify that permission is granted
        args = self.permission_test_view_args
        kwargs = self.permission_test_view_kwargs

        try:
            response = view(request, *args, **kwargs)
        except PermissionDenied:
            self.fail("Failed to access view with user privileges: %s" % str(self.sufficient_permissions))

        self.assertEqual(response.status_code, 200)

    def test_permission_denied(self):
        # Set-up a request from user with insufficient privileges.
        request = RequestFactory().get("/fake-path")
        request.user = User.objects.create(username="user", password="password")

        # Get the view.
        if self.view_class:
            view = self.view_class.as_view()
        elif self.view_function:
            view = self.view_function

        # Verify that permission is denied.
        args = self.permission_test_view_args
        kwargs = self.permission_test_view_kwargs
        self.assertRaises(PermissionDenied, view, request, *args, **kwargs)


class FakeMessages(object):
    """
    Helper class for mocking the Django messages framework.
    """

    def __init__(self):
        """
        Initalises the message framework mocker.

        Set-ups the messages list prpoperty.
        """
        self.messages = []

    def add(self, level, message, extra_tags):
        """
        Adds a message.
        """

        self.messages.append(message)
