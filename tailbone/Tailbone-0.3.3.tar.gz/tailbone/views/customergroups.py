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
CustomerGroup Views
"""

from . import SearchableAlchemyGridView, CrudView

from ..db import Session
from rattail.db.model import CustomerGroup, CustomerGroupAssignment


class CustomerGroupsGrid(SearchableAlchemyGridView):

    mapped_class = CustomerGroup
    config_prefix = 'customer_groups'
    sort = 'name'

    def filter_map(self):
        return self.make_filter_map(ilike=['name'])

    def filter_config(self):
        return self.make_filter_config(
            include_filter_name=True,
            filter_type_name='lk')

    def sort_map(self):
        return self.make_sort_map('id', 'name')

    def grid(self):
        g = self.make_grid()
        g.configure(
            include=[
                g.id.label("ID"),
                g.name,
                ],
            readonly=True)
        if self.request.has_perm('customer_groups.read'):
            g.viewable = True
            g.view_route_name = 'customer_group.read'
        if self.request.has_perm('customer_groups.update'):
            g.editable = True
            g.edit_route_name = 'customer_group.update'
        if self.request.has_perm('customer_groups.delete'):
            g.deletable = True
            g.delete_route_name = 'customer_group.delete'
        return g


class CustomerGroupCrud(CrudView):

    mapped_class = CustomerGroup
    home_route = 'customer_groups'
    pretty_name = "Customer Group"

    def fieldset(self, model):
        fs = self.make_fieldset(model)
        fs.configure(
            include=[
                fs.id.label("ID"),
                fs.name,
                ])
        return fs

    def pre_delete(self, group):
        # First remove customer associations.
        q = Session.query(CustomerGroupAssignment)\
            .filter(CustomerGroupAssignment.group == group)
        for assignment in q:
            Session.delete(assignment)


def add_routes(config):
    config.add_route('customer_groups',         '/customer-groups')
    config.add_route('customer_group.create',   '/customer-groups/new')
    config.add_route('customer_group.read',     '/customer-groups/{uuid}')
    config.add_route('customer_group.update',   '/customer-groups/{uuid}/edit')
    config.add_route('customer_group.delete',   '/customer-groups/{uuid}/delete')


def includeme(config):
    add_routes(config)

    config.add_view(CustomerGroupsGrid, route_name='customer_groups',
                    renderer='/customergroups/index.mako',
                    permission='customer_groups.list')
    config.add_view(CustomerGroupCrud, attr='create', route_name='customer_group.create',
                    renderer='/customergroups/crud.mako',
                    permission='customer_groups.create')
    config.add_view(CustomerGroupCrud, attr='read', route_name='customer_group.read',
                    renderer='/customergroups/crud.mako',
                    permission='customer_groups.read')
    config.add_view(CustomerGroupCrud, attr='update', route_name='customer_group.update',
                    renderer='/customergroups/crud.mako',
                    permission='customer_groups.update')
    config.add_view(CustomerGroupCrud, attr='delete', route_name='customer_group.delete',
                    permission='customer_groups.delete')
