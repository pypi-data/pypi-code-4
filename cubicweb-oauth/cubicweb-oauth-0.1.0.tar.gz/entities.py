# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-oauth entity's classes"""
from rauth import OAuth2Service

from cubicweb.predicates import is_instance
from cubicweb.appobject import AppObject
from cubicweb.view import EntityAdapter


class Provider(AppObject):
    __registry__ = 'provider'
    __abstract__ = True


class FacebookProvider(Provider):
    __regid__ = 'facebook'
    authorize_url = 'https://graph.facebook.com/oauth/authorize'
    access_token_url = 'https://graph.facebook.com/oauth/access_token'
    base_url = 'https://graph.facebook.com/'
    scope = 'email'

    def retrieve_info(self, request):
        me = request.get(
            'me?fields=name,first_name,last_name,email,username'
        ).json()
        return {
            'uid': me['id'],
            'email': me['email'],
            'firstname': me['first_name'],
            'lastname': me['last_name'],
            'username': me['username']
        }


class ServiceAdapter(EntityAdapter):
    __regid__ = 'externalauth.service'
    __select__ = is_instance('ExternalAuthService')

    @property
    def provider(self):
        spid = self.entity.provider[0].spid
        return self._cw.vreg['provider'][spid][0](self._cw)

    @property
    def oauth2_service(self):
        provider = self.provider
        return OAuth2Service(
            name=self.entity.application_name,
            client_id=self.entity.application_id,
            client_secret=self.entity.application_secret,
            authorize_url=provider.authorize_url,
            access_token_url=provider.access_token_url,
            base_url=provider.base_url,
        )
