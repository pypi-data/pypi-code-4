__metaclass__ = type

import time
import base64

from django.conf import settings
from django.contrib.auth.models import User
from openid.consumer.consumer import SUCCESS
from openid.extensions import ax, sreg

from .constants import AX_MAPPINGS, AX_IS_VERIFIED
from .models import UserOpenID


class IdentityAlreadyClaimed(Exception):
    pass


class OpenIDBackend(object):

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, **kwargs):
        openid_response = kwargs.get('openid_response')
        if openid_response is None:
            return None

        if openid_response.status != SUCCESS:
            return None

        user = None
        user_openid = UserOpenID.by_identity_url(openid_response.identity_url)
        if not user_openid:
            # XXX: because of migrating from UUA to UUB the identity_url might
            # be diferrent when comming here from UUB so we try to get the
            # record by email
            user_openid = UserOpenID.by_user_email(
                self._get_email(openid_response)
            )
            if user_openid:
                user_openid.update_openid_identifiers(
                    claimed_id=openid_response.identity_url,
                    display_id=openid_response.endpoint.getDisplayIdentifier()
                )
        if not user_openid and settings.OPENID_CREATE_USERS:
            user = self.create_user_from_openid(openid_response)

        user = user or getattr(user_openid, 'user')

        if user and settings.OPENID_UPDATE_DETAILS_FROM_SREG:
            self.update_user_details_from_sreg(user, openid_response)

        return user

    def create_user_from_openid(self, openid_response):
        email = self._get_email(openid_response)
        username = base64.b64encode(str(time.time())).replace('=', '')
        user = User.objects.create_user(username, email)
        user.first_name = self._get_first_name(openid_response)
        user.last_name = self._get_last_name(openid_response)
        user.save()
        self.associate_openid(user, openid_response)
        return user

    def associate_openid(self, user, openid_response):
        user_openid = UserOpenID.by_identity_url(openid_response.identity_url)
        if not user_openid:
            user_openid = UserOpenID(
                user=user,
                claimed_id=openid_response.identity_url,
                display_id=openid_response.endpoint.getDisplayIdentifier()
            )
            user_openid.save()
        if user_openid.user != user:
            raise IdentityAlreadyClaimed(
                "The identity %s has already been claimed"
                % openid_response.identity_url
            )

        return user_openid

    def update_user_details_from_sreg(self, user, openid_response):
        user.first_name = self._get_first_name(openid_response)
        user.last_name = self._get_last_name(openid_response)
        user.save()

    def _update_claimed_id(self, user_openid, openid_response):
        user_openid.claimed_id = openid_response.identity_url
        user_openid.save()

    def _get_sreg(self, openid_response):
        return sreg.SRegResponse.fromSuccessResponse(openid_response)

    def _get_email(self, openid_response):
        sreg = self._get_sreg(openid_response)
        return sreg.get('email')

    def _get_full_name(self, openid_response):
        sreg = self._get_sreg(openid_response)
        return sreg.get('fullname')

    def _get_first_name(self, openid_response):
        fullname = self._get_full_name(openid_response)
        if ' ' in fullname:
            first_name, _, _ = fullname.rpartition(' ')
            return first_name
        return ''

    def _get_last_name(self, openid_response):
        fullname = self._get_full_name(openid_response)
        if ' ' in fullname:
            _, _, last_name = fullname.rpartition(' ')
            return last_name
        return fullname

    def _get_ax(self, openid_response):
        return ax.FetchResponse.fromSuccessResponse(openid_response)

    def _get_is_verified(self, openid_response):
        ax_response = self._get_ax(openid_response)
        ax_is_verified = ax_response.get(AX_MAPPINGS[AX_IS_VERIFIED][0])[0]
        if ax_is_verified == u'True':
            return True
        return False