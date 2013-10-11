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
Subdepartment Views
"""

from . import SearchableAlchemyGridView, CrudView

from rattail.db.model import Subdepartment


class SubdepartmentsGrid(SearchableAlchemyGridView):

    mapped_class = Subdepartment
    config_prefix = 'subdepartments'
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
                g.department,
                ],
            readonly=True)
        if self.request.has_perm('subdepartments.read'):
            g.viewable = True
            g.view_route_name = 'subdepartment.read'
        if self.request.has_perm('subdepartments.update'):
            g.editable = True
            g.edit_route_name = 'subdepartment.update'
        if self.request.has_perm('subdepartments.delete'):
            g.deletable = True
            g.delete_route_name = 'subdepartment.delete'
        return g


class SubdepartmentCrud(CrudView):
    
    mapped_class = Subdepartment
    home_route = 'subdepartments'

    def fieldset(self, model):
        fs = self.make_fieldset(model)
        fs.configure(
            include=[
                fs.number,
                fs.name,
                fs.department,
                ])
        return fs


def includeme(config):

    config.add_route('subdepartments', '/subdepartments')
    config.add_view(SubdepartmentsGrid, route_name='subdepartments',
                    renderer='/subdepartments/index.mako',
                    permission='subdepartments.list')

    config.add_route('subdepartment.create', '/subdepartments/new')
    config.add_view(SubdepartmentCrud, attr='create',
                    route_name='subdepartment.create',
                    renderer='/subdepartments/crud.mako',
                    permission='subdepartments.create')

    config.add_route('subdepartment.read', '/subdepartments/{uuid}')
    config.add_view(SubdepartmentCrud, attr='read',
                    route_name='subdepartment.read',
                    renderer='/subdepartments/crud.mako',
                    permission='subdepartments.read')

    config.add_route('subdepartment.update', '/subdepartments/{uuid}/edit')
    config.add_view(SubdepartmentCrud, attr='update',
                    route_name='subdepartment.update',
                    renderer='/subdepartments/crud.mako',
                    permission='subdepartments.update')

    config.add_route('subdepartment.delete', '/subdepartments/{uuid}/delete')
    config.add_view(SubdepartmentCrud, attr='delete',
                    route_name='subdepartment.delete',
                    permission='subdepartments.delete')
