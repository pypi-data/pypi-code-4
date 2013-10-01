# -*- coding: utf-8 -*-
#
# copyright 2013 Unlish (Montpellier, FRANCE), all rights reserved.
# contact http://www.unlish.com -- mailto:contact@unlish.com
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

"""cubicweb-oauth schema."""

from yams.buildobjs import (
    String, EntityType, SubjectRelation, Datetime, Boolean
)

from cubicweb.schema import ERQLExpression


# TODO set the maxsize of the String attributes.

sp_attrs_perms = {
    'read': ('managers', 'users', 'guests'),
    'update': ('managers',),
}


class ExternalAuthProvider(EntityType):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers',),
        'update': ('managers',),
        'delete': ('managers',)
    }
    spid = String(
        __permissions__=sp_attrs_perms,
        maxsize=16, required=True, unique=True,
        description="Provider unique id ('facebook', 'twitter')")
    name = String(
        __permissions__=sp_attrs_perms,
        maxsize=16, required=True, unique=True,
        description="Provider user-friendly name ('Facebook', 'Twitter')")


# XXX make it workfloable
class ExternalAuthService(EntityType):
    __permissions__ = {
        'read': ('managers',),
        'add': ('managers',),
        'update': ('managers',),
        'delete': ('managers',),
    }
    __unique_together__ = [
        ('provider', 'application_id'),
    ]
    provider = SubjectRelation(
        'ExternalAuthProvider',
        __permissions__={
            'read': ('managers',),
            'add': ('managers',),
            'delete': ('managers',)
        },
        cardinality='1*',
        inlined=True
    )
    application_name = String(
        maxsize=64, description="Application name",
        __permissions__=sp_attrs_perms)
    application_id = String(
        maxsize=64, description="OAuth2 client_id.",
        __permissions__=sp_attrs_perms)
    application_secret = String(
        maxsize=64, description="OAuth2 client_secret",
        __permissions__=sp_attrs_perms)


class ExternalIdentity(EntityType):
    __permissions__ = {
        'read':   ('managers', ERQLExpression('X identity_of U')),
        'add':    ('managers',),
        'update': ('managers',),
        'delete': ('managers', ERQLExpression('X identity_of U'))
    }
    __unique_together__ = [('provider', 'uid')]
    provider = SubjectRelation(
        'ExternalAuthProvider', cardinality='1*', inlined=True,
        __permissions__={
            'read': ('managers', 'users'),
            'add': ('managers',),
            'delete': ('managers',)
        }
    )
    identity_of = SubjectRelation(
        'CWUser', cardinality='?*', inlined=True,
        __permissions__={
            'read':   ('managers', 'users',),
            'add':    ('managers',),
            'delete': ('managers',)
        }
    )
    uid = String(
        required=True,
        __permissions__={
            'read':   ('managers', 'users',),
            'update': ('managers',),
        }
    )


class OAuth2Session(EntityType):
    __permissions__ = {
        'read':   ('managers', ERQLExpression('X external_identity I, I identity_of U')),
        'add':    ('managers',),
        'update': ('managers',),
        'delete': ('managers', ERQLExpression('X external_identity I, I identity_of U'))
    }

    external_identity = SubjectRelation(
        'ExternalIdentity', cardinality='1*', inlined=True,
        __permissions__={
            'read':   ('managers', 'users',),
            'add':    ('managers',),
            'delete': ('managers',)
        }
    )
    service = SubjectRelation(
        'ExternalAuthService', cardinality='1*', inlined=True,
        __permissions__={
            'read':   ('managers', 'users',),
            'add':    ('managers',),
            'delete': ('managers',)
        }
    )
    access_token = String(required=True, unique=True)
    active = Boolean(required=True, default=True)
    expiry = Datetime()
