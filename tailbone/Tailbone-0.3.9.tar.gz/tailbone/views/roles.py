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
Role Views
"""

from . import SearchableAlchemyGridView, CrudView
from pyramid.httpexceptions import HTTPFound

from ..db import Session
from rattail.db.model import Role
from rattail.db.auth import has_permission, administrator_role, guest_role

import formalchemy
from webhelpers.html import tags
from webhelpers.html import HTML


default_permissions = [
    ("Batches", [
            ('batches.list',                    "List Batches"),
            ('batches.read',                    "View Batches"),
            ('batches.create',                  "Create Batches"),
            ('batches.update',                  "Edit Batches"),
            ('batches.delete',                  "Delete Batches"),
            ('batches.execute',                 "Execute Batches"),
            ('batch_rows.read',                 "View Batch Rows"),
            ('batch_rows.update',               "Edit Batch Rows"),
            ('batch_rows.delete',               "Delete Batch Rows"),
            ]),
    ("Brands", [
            ('brands.list',                     "List Brands"),
            ('brands.read',                     "View Brands"),
            ('brands.create',                   "Create Brands"),
            ('brands.update',                   "Edit Brands"),
            ('brands.delete',                   "Delete Brands"),
            ('brands.force_sync',               "Forcibly Sync Brands"),
            ]),
    ("Customers", [
            ('customers.list',                  "List Customers"),
            ('customers.read',                  "View Customers"),
            ('customers.force_sync',            "Forcibly Sync Customers"),
            ('customer_groups.list',            "List Customer Groups"),
            ('customer_groups.read',            "View Customer Groups"),
            ('customer_groups.force_sync',      "Forcibly Sync Customer Groups"),
            ]),
    ("Departments", [
            ('departments.list',                "List Departments"),
            ('departments.read',                "View Departments"),
            ('departments.create',              "Create Departments"),
            ('departments.update',              "Edit Departments"),
            ('departments.delete',              "Delete Departments"),
            ('departments.force_sync',          "Forcibly Sync Departments"),
            ]),
    ("Employees", [
            ('employees.list',                  "List Employees"),
            ('employees.force_sync',            "Forcibly Sync Employees"),
            ]),
    ("Label Profiles", [
            ('label_profiles.list',             "List Label Profiles"),
            ('label_profiles.view',             "View Label Profiles"),
            ('label_profiles.create',           "Create Label Profiles"),
            ('label_profiles.update',           "Edit Label Profiles"),
            ('label_profiles.delete',           "Delete Label Profiles"),
            ]),
    ("People", [
            ('people.list',                     "List People"),
            ('people.read',                     "View People"),
            ('people.create',                   "Create People"),
            ('people.update',                   "Edit People"),
            ('people.delete',                   "Delete People"),
            ('people.force_sync',               "Forcibly Sync People"),
            ]),
    ("Products", [
            ('products.list',                   "List Products"),
            ('products.read',                   "View Products"),
            ('products.create',                 "Create Products"),
            ('products.update',                 "Edit Products"),
            ('products.delete',                 "Delete Products"),
            ('products.print_labels',           "Print Product Labels"),
            ('products.force_sync',             "Forcibly Sync Products"),
            ]),
    ("Roles", [
            ('roles.list',                      "List Roles"),
            ('roles.read',                      "View Roles"),
            ('roles.create',                    "Create Roles"),
            ('roles.update',                    "Edit Roles"),
            ('roles.delete',                    "Delete Roles"),
            ]),
    ("Stores", [
            ('stores.list',                     "List Stores"),
            ('stores.read',                     "View Stores"),
            ('stores.create',                   "Create Stores"),
            ('stores.update',                   "Edit Stores"),
            ('stores.delete',                   "Delete Stores"),
            ('stores.force_sync',               "Forcibly Sync Stores"),
            ]),
    ("Subdepartments", [
            ('subdepartments.list',             "List Subdepartments"),
            ('subdepartments.read',             "View Subdepartments"),
            ('subdepartments.create',           "Create Subdepartments"),
            ('subdepartments.update',           "Edit Subdepartments"),
            ('subdepartments.delete',           "Delete Subdepartments"),
            ('subdepartments.force_sync',       "Forcibly Sync Subdepartments"),
            ]),
    ("Users", [
            ('users.list',                      "List Users"),
            ('users.read',                      "View Users"),
            ('users.create',                    "Create Users"),
            ('users.update',                    "Edit Users"),
            ('users.delete',                    "Delete Users"),
            ('users.force_sync',                "Forcibly Sync Users"),
            ]),
    ("Vendors", [
            ('vendors.list',                    "List Vendors"),
            ('vendors.read',                    "View Vendors"),
            ('vendors.create',                  "Create Vendors"),
            ('vendors.update',                  "Edit Vendors"),
            ('vendors.delete',                  "Delete Vendors"),
            ('vendors.import_catalog',          "Import Vendor Catalogs"),
            ('vendors.force_sync',              "Forcibly Sync Vendors"),
            ]),
    ]


class RolesGrid(SearchableAlchemyGridView):

    mapped_class = Role
    config_prefix = 'roles'
    sort = 'name'

    def filter_map(self):
        return self.make_filter_map(ilike=['name'])

    def filter_config(self):
        return self.make_filter_config(
            include_filter_name=True,
            filter_type_name='lk')

    def sort_map(self):
        return self.make_sort_map('name')

    def grid(self):
        g = self.make_grid()
        g.configure(
            include=[
                g.name,
                ],
            readonly=True)
        if self.request.has_perm('roles.read'):
            g.viewable = True
            g.view_route_name = 'role.read'
        if self.request.has_perm('roles.update'):
            g.editable = True
            g.edit_route_name = 'role.update'
        if self.request.has_perm('roles.delete'):
            g.deletable = True
            g.delete_route_name = 'role.delete'
        return g


class PermissionsField(formalchemy.Field):

    def sync(self):
        if not self.is_readonly():
            role = self.model
            role.permissions = self.renderer.deserialize()


def PermissionsFieldRenderer(permissions, *args, **kwargs):

    perms = permissions
    
    class PermissionsFieldRenderer(formalchemy.FieldRenderer):

        permissions = perms

        def deserialize(self):
            perms = []
            i = len(self.name) + 1
            for key in self.params:
                if key.startswith(self.name):
                    perms.append(key[i:])
            return perms

        def _render(self, readonly=False, **kwargs):
            role = self.field.model
            admin = administrator_role(Session())
            if role is admin:
                html = HTML.tag('p', c="This is the administrative role; "
                                "it has full access to the entire system.")
                if not readonly:
                    html += tags.hidden(self.name, value='') # ugly hack..or good idea?
            else:
                html = ''
                for group, perms in self.permissions:
                    inner = HTML.tag('p', c=group)
                    for perm, title in perms:
                        checked = has_permission(
                            Session(), role, perm, include_guest=False)
                        if readonly:
                            span = HTML.tag('span', c="[X]" if checked else "[ ]")
                            inner += HTML.tag('p', class_='perm', c=span + ' ' + title)
                        else:
                            inner += tags.checkbox(self.name + '-' + perm,
                                                   checked=checked, label=title)
                    html += HTML.tag('div', class_='group', c=inner)
            return html

        def render(self, **kwargs):
            return self._render(**kwargs)

        def render_readonly(self, **kwargs):
            return self._render(readonly=True, **kwargs)

    return PermissionsFieldRenderer


class RoleCrud(CrudView):

    mapped_class = Role
    home_route = 'roles'
    permissions = default_permissions

    def fieldset(self, role):
        fs = self.make_fieldset(role)
        fs.append(PermissionsField(
                'permissions',
                renderer=PermissionsFieldRenderer(self.permissions)))
        fs.configure(
            include=[
                fs.name,
                fs.permissions,
                ])
        return fs

    def pre_delete(self, model):
        admin = administrator_role(Session())
        guest = guest_role(Session())
        if model in (admin, guest):
            self.request.session.flash("You may not delete the %s role." % str(model), 'error')
            return HTTPFound(location=self.request.get_referrer())


def includeme(config):
    
    config.add_route('roles', '/roles')
    config.add_view(RolesGrid, route_name='roles',
                    renderer='/roles/index.mako',
                    permission='roles.list')

    settings = config.get_settings()
    perms = settings.get('edbob.permissions')
    if perms:
        RoleCrud.permissions = perms

    config.add_route('role.create', '/roles/new')
    config.add_view(RoleCrud, attr='create', route_name='role.create',
                    renderer='/roles/crud.mako',
                    permission='roles.create')

    config.add_route('role.read', '/roles/{uuid}')
    config.add_view(RoleCrud, attr='read', route_name='role.read',
                    renderer='/roles/crud.mako',
                    permission='roles.read')

    config.add_route('role.update', '/roles/{uuid}/edit')
    config.add_view(RoleCrud, attr='update', route_name='role.update',
                    renderer='/roles/crud.mako',
                    permission='roles.update')

    config.add_route('role.delete', '/roles/{uuid}/delete')
    config.add_view(RoleCrud, attr='delete', route_name='role.delete',
                    permission='roles.delete')
