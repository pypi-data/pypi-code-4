import unittest

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client, RequestFactory
from django.test.utils import override_settings
import mock
from openid import message
from openid.consumer.consumer import SUCCESS, SuccessResponse, FailureResponse
from openid.consumer.discover import OpenIDServiceEndpoint
from openid.extensions.sreg import SRegRequest

from .auth import OpenIDBackend
from .forms import ChangePasswordForm
from .models import UserOpenID
from .views import (reverse_ax_mapper, ax_change_complete,
                    build_return_to_url)


class MockOpenIDSuccessResponse(SuccessResponse):
    def __init__(self, status, identity_url):
        self.status = status
        self.identity_url = identity_url
        self.message = message.Message()

        sreg_ext = SRegRequest(
            required=['nickname', 'email'],
            optional=['fullname'],
            policy_url=None,
            sreg_ns_uri='http://openid.net/extensions/sreg/1.1'
        )
        sreg_ext.toMessage(self.message)
        self.signed_fields = ['openid.sreg.nickname', 'openid.sreg.email',
                              'openid.sreg.required', 'openid.sreg.optional',
                              'openid.sreg.fullname']

        self.endpoint = OpenIDServiceEndpoint()
        self.endpoint.claimed_id = identity_url

    def addSRegValid(self):
        self.message.setArg(
            'http://openid.net/extensions/sreg/1.1', 'nickname', 'MyNickname'
        )
        self.message.setArg(
            'http://openid.net/extensions/sreg/1.1', 'email', 'user@domain.com'
        )
        self.message.setArg(
            'http://openid.net/extensions/sreg/1.1', 'fullname', 'Full Name'
        )

    def extensionResponse(self, *args):
        return {}


class MockOpenIdFailureResponse(FailureResponse):
    pass


class OpenIDFlowTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.backend = OpenIDBackend()

    def test_get_user(self):
        user = self.backend.get_user(-1)
        self.failUnlessEqual(user, None)

        user = self.backend.get_user(2)
        self.failUnlessEqual(user.username, "admin")

    def test_authenticate_fail(self):
        try:
            user = self.backend.authenticate(openid_response=None)
            self.failUnlessEqual(user, None)
        except:
            pass

    def test_create_user_from_openid_with_sreg(self):
        openid_response = MockOpenIDSuccessResponse(
            SUCCESS, 'http://192.168.1.121:8081/u/some_identity'
        )
        openid_response.addSRegValid()
        user = self.backend.authenticate(openid_response=openid_response)
        self.assertEquals(user.first_name, 'Full')
        self.assertEquals(user.last_name, 'Name')

    def test_create_user_from_openid(self):
        openid_response = MockOpenIDSuccessResponse(
            SUCCESS, 'http://192.168.1.121:8081/u/some_identity'
        )
        user = self.backend.authenticate(openid_response=openid_response)
        self.assertEquals(user.email, 'user@domain.com')

    def test_openid_request_failure_response(self):
        openid_response = MockOpenIdFailureResponse(
            endpoint=OpenIDServiceEndpoint()
        )
        user = self.backend.authenticate(openid_response=openid_response)
        self.assertEquals(user, None)


class UserOpenIDTestCase(TestCase):

    def test_delete_user(self):
        # Create a user and an OpenID user associated
        user1 = User.objects.create(username="test1")
        user2 = User.objects.create(username="test2")
        openiduser = UserOpenID.objects.create(
            user=user1,
            claimed_id="http://192.168.1.121:8081/u/BdwAEHKnlO_W3zOWh0TMcQ",
            display_id="http://192.168.1.121:8081/u/BdwAEHKnlO_W3zOWh0TMcQ"
        )

        # Delete the user and check if the OpenID user is deleted
        user1.delete()
        self.assertRaises(
            UserOpenID.DoesNotExist,
            lambda: UserOpenID.objects.get(pk=openiduser.pk))

        # Delete the second user. It must be done gracefully.
        user2.delete()


class TestReverseAXMapper(unittest.TestCase):

    def setUp(self):
        self.data = {"first_name": "Foo",
                     "last_name": "Bar",
                     "email": "qux@foo.com",
                     "zip_code": "90210"}

    def test_profile_fields_are_mapped(self):
        ax_data = reverse_ax_mapper(self.data)
        self.assertEqual(len(ax_data), len(self.data))

    def test_mapping_to_ax_alias(self):
        ax_data = reverse_ax_mapper(self.data)
        postal_code = filter(lambda data: data.value == "90210",
                             ax_data)
        self.assertEqual(len(postal_code), 1)
        zip_code = postal_code[0]
        self.assertEqual(zip_code.ax_alias,
                         'http://openid.net/schema/contact/postalcode/home')

        self.assertEqual(zip_code.value, "90210")
        self.assertEqual(zip_code.field_name, "zip_code")

    def test_invalid_names_are_skipped(self):
        self.data["invalid_key"] = "weird value"
        ax_data = reverse_ax_mapper(self.data)
        self.assertEqual(len(ax_data), 4)
        invalid_key = filter(lambda data: data.field_name == "invalid_key",
                             ax_data)
        self.assertEqual(len(invalid_key), 0)


class ChangePasswordFormTest(unittest.TestCase):

    def test_new_password_must_match(self):
        data = {"old_password": "old passwd",
                "new_password": "newpass",
                "new_password_again": "newpass_wrong"}
        form = ChangePasswordForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["__all__"],
                         ["New passwords do not match"])

    def test_confirmation_password_not_filled_in(self):
        data = {"old_password": "old passwd",
                "new_password": "newpass"}
        form = ChangePasswordForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password_again', form.errors)

    def test_valid_form(self):
        data = {"old_password": "old passwd",
                "new_password": "newpass",
                "new_password_again": "newpass"}
        form = ChangePasswordForm(data)
        self.assertTrue(form.is_valid())


class ReturnURLTest(TestCase):

    def setUp(self):
        super(ReturnURLTest, self).setUp()
        self.factory = RequestFactory()

    @override_settings(OPENID_CUSTOM_RETURN_TO="http://ab.c/path")
    def test_custom_return_to(self):
        return_url = build_return_to_url(None, ax_change_complete,
                                         'next', '/back')
        self.assertEqual(
            return_url,
            "http://ab.c/path/uua/change_password/complete?next=%2Fback")

    def test_return_to_usual_domain(self):
        view_url = "http://localhost/uua/change_password/complete"
        request = mock.Mock()
        request.build_absolute_uri.return_value = view_url

        return_url = build_return_to_url(request, ax_change_complete,
                                         'next', '/back')
        self.assertEqual(
            return_url,
            "http://localhost/uua/change_password/complete?next=%2Fback")
