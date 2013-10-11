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
Department Views
"""


from . import SearchableAlchemyGridView, CrudView, AlchemyGridView, AutocompleteView

from rattail.db.model import Department, Product, ProductCost, Vendor


class DepartmentsGrid(SearchableAlchemyGridView):

    mapped_class = Department
    config_prefix = 'departments'
    sort = 'name'

    def filter_map(self):
        return self.make_filter_map(ilike=['name'])

    def filter_config(self):
        return self.make_filter_config(
            include_filter_name=True,
            filter_type_name='lk')

    def sort_map(self):
        return self.make_sort_map('number', 'name')

    def grid(self):
        g = self.make_grid()
        g.configure(
            include=[
                g.number,
                g.name,
                ],
            readonly=True)
        if self.request.has_perm('departments.read'):
            g.viewable = True
            g.view_route_name = 'department.read'
        if self.request.has_perm('departments.update'):
            g.editable = True
            g.edit_route_name = 'department.update'
        if self.request.has_perm('departments.delete'):
            g.deletable = True
            g.delete_route_name = 'department.delete'
        return g


class DepartmentCrud(CrudView):
    
    mapped_class = Department
    home_route = 'departments'

    def fieldset(self, model):
        fs = self.make_fieldset(model)
        fs.configure(
            include=[
                fs.number,
                fs.name,
                ])
        return fs


class DepartmentsByVendorGrid(AlchemyGridView):

    mapped_class = Department
    config_prefix = 'departments.by_vendor'
    checkboxes = True
    partial_only = True

    def query(self):
        q = self.make_query()
        q = q.outerjoin(Product)
        q = q.join(ProductCost)
        q = q.join(Vendor)
        q = q.filter(Vendor.uuid == self.request.params['uuid'])
        q = q.distinct()
        q = q.order_by(Department.name)
        return q

    def grid(self):
        g = self.make_grid()
        g.configure(
            include=[
                g.name,
                ],
            readonly=True)
        return g


class DepartmentsAutocomplete(AutocompleteView):

    mapped_class = Department
    fieldname = 'name'


def includeme(config):

    config.add_route('departments', '/departments')
    config.add_view(DepartmentsGrid,
                    route_name='departments',
                    renderer='/departments/index.mako',
                    permission='departments.list')

    config.add_route('departments.autocomplete', '/departments/autocomplete')
    config.add_view(DepartmentsAutocomplete,
                    route_name='departments.autocomplete',
                    renderer='json',
                    permission='departments.list')

    config.add_route('departments.by_vendor', '/departments/by-vendor')
    config.add_view(DepartmentsByVendorGrid,
                    route_name='departments.by_vendor',
                    permission='departments.list')

    config.add_route('department.create', '/departments/new')
    config.add_view(DepartmentCrud, attr='create',
                    route_name='department.create',
                    renderer='/departments/crud.mako',
                    permission='departments.create')

    config.add_route('department.read', '/departments/{uuid}')
    config.add_view(DepartmentCrud, attr='read',
                    route_name='department.read',
                    renderer='/departments/crud.mako',
                    permission='departments.read')

    config.add_route('department.update', '/departments/{uuid}/edit')
    config.add_view(DepartmentCrud, attr='update',
                    route_name='department.update',
                    renderer='/departments/crud.mako',
                    permission='departments.update')

    config.add_route('department.delete', '/departments/{uuid}/delete')
    config.add_view(DepartmentCrud, attr='delete',
                    route_name='department.delete',
                    permission='departments.delete')
