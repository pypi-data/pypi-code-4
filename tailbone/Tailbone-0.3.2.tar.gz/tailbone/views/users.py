#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
User Views
"""

import formalchemy

from edbob.pyramid.views import users

from . import SearchableAlchemyGridView, CrudView
from ..forms import PersonFieldRenderer
from rattail.db.model import User, Person


class UsersGrid(SearchableAlchemyGridView):

    mapped_class = User
    config_prefix = 'users'
    sort = 'username'

    def join_map(self):
        return {
            'person':
                lambda q: q.outerjoin(Person),
            }

    def filter_map(self):
        return self.make_filter_map(
            ilike=['username'],
            person=self.filter_ilike(Person.display_name))

    def filter_config(self):
        return self.make_filter_config(
            include_filter_username=True,
            filter_type_username='lk',
            include_filter_person=True,
            filter_type_person='lk')

    def sort_map(self):
        return self.make_sort_map(
            'username',
            person=self.sorter(Person.display_name))

    def grid(self):
        g = self.make_grid()
        g.configure(
            include=[
                g.username,
                g.person,
                ],
            readonly=True)
        if self.request.has_perm('users.read'):
            g.viewable = True
            g.view_route_name = 'user.read'
        if self.request.has_perm('users.update'):
            g.editable = True
            g.edit_route_name = 'user.update'
        if self.request.has_perm('users.delete'):
            g.deletable = True
            g.delete_route_name = 'user.delete'
        return g


class UserCrud(CrudView):

    mapped_class = User
    home_route = 'users'

    def fieldset(self, user):
        fs = self.make_fieldset(user)

        # Must set Person options to empty set to avoid unwanted magic.
        fs.person.set(options=[])
        fs.person.set(renderer=PersonFieldRenderer(
                self.request.route_url('people.autocomplete')))

        fs.append(users.PasswordField('password'))
        fs.append(formalchemy.Field(
                'confirm_password', renderer=users.PasswordFieldRenderer))
        fs.append(users.RolesField(
                'roles', renderer=users.RolesFieldRenderer(self.request)))

        fs.configure(
            include=[
                fs.username,
                fs.person,
                fs.password.label("Set Password"),
                fs.confirm_password,
                fs.roles,
                ])

        if self.readonly:
            del fs.password
            del fs.confirm_password

        return fs


def includeme(config):

    config.add_route('users', '/users')
    config.add_view(UsersGrid, route_name='users',
                    renderer='/users/index.mako',
                    permission='users.list')

    config.add_route('user.create', '/users/new')
    config.add_view(UserCrud, attr='create', route_name='user.create',
                    renderer='/users/crud.mako',
                    permission='users.create')

    config.add_route('user.read', '/users/{uuid}')
    config.add_view(UserCrud, attr='read', route_name='user.read',
                    renderer='/users/crud.mako',
                    permission='users.read')

    config.add_route('user.update', '/users/{uuid}/edit')
    config.add_view(UserCrud, attr='update', route_name='user.update',
                    renderer='/users/crud.mako',
                    permission='users.update')

    config.add_route('user.delete', '/users/{uuid}/delete')
    config.add_view(UserCrud, attr='delete', route_name='user.delete',
                    permission='users.delete')
