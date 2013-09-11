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
Employee Views
"""

from sqlalchemy import and_

from . import SearchableAlchemyGridView, CrudView
from ..grids.search import EnumSearchFilter
from ..forms import AssociationProxyField, EnumFieldRenderer
from rattail.db.model import (
    Employee, EmployeePhoneNumber, EmployeeEmailAddress, Person)
from rattail.enum import EMPLOYEE_STATUS, EMPLOYEE_STATUS_CURRENT


class EmployeesGrid(SearchableAlchemyGridView):

    mapped_class = Employee
    config_prefix = 'employees'
    sort = 'first_name'

    def join_map(self):
        return {
            'phone':
                lambda q: q.outerjoin(EmployeePhoneNumber, and_(
                    EmployeePhoneNumber.parent_uuid == Employee.uuid,
                    EmployeePhoneNumber.preference == 1)),
            'email':
                lambda q: q.outerjoin(EmployeeEmailAddress, and_(
                    EmployeeEmailAddress.parent_uuid == Employee.uuid,
                    EmployeeEmailAddress.preference == 1)),
            }

    def filter_map(self):
        kwargs = dict(
            first_name=self.filter_ilike(Person.first_name),
            last_name=self.filter_ilike(Person.last_name),
            phone=self.filter_ilike(EmployeePhoneNumber.number),
            email=self.filter_ilike(EmployeeEmailAddress.address))
        if self.request.has_perm('employees.edit'):
            kwargs.update(dict(
                    exact=['id', 'status']))
        return self.make_filter_map(**kwargs)

    def filter_config(self):
        kwargs = dict(
            include_filter_first_name=True,
            filter_type_first_name='lk',
            include_filter_last_name=True,
            filter_type_last_name='lk',
            filter_label_phone="Phone Number",
            filter_label_email="Email Address")
        if self.request.has_perm('employees.edit'):
            kwargs.update(dict(
                    filter_label_id="ID",
                    include_filter_status=True,
                    filter_type_status='is',
                    filter_factory_status=EnumSearchFilter(EMPLOYEE_STATUS),
                    status=EMPLOYEE_STATUS_CURRENT))
        return self.make_filter_config(**kwargs)

    def sort_map(self):
        return self.make_sort_map(
            first_name=self.sorter(Person.first_name),
            last_name=self.sorter(Person.last_name),
            phone=self.sorter(EmployeePhoneNumber.number),
            email=self.sorter(EmployeeEmailAddress.address))

    def query(self):
        q = self.make_query()
        q = q.join(Person)
        if not self.request.has_perm('employees.edit'):
            q = q.filter(Employee.status == EMPLOYEE_STATUS_CURRENT)
        return q

    def grid(self):
        g = self.make_grid()
        g.append(AssociationProxyField('first_name'))
        g.append(AssociationProxyField('last_name'))
        g.configure(
            include=[
                g.id.label("ID"),
                g.first_name,
                g.last_name,
                g.phone.label("Phone Number"),
                g.email.label("Email Address"),
                g.status.with_renderer(EnumFieldRenderer(EMPLOYEE_STATUS)),
                ],
            readonly=True)

        # Hide ID and Status fields for unprivileged users.
        if not self.request.has_perm('employees.edit'):
            del g.id
            del g.status

        if self.request.has_perm('employees.read'):
            g.viewable = True
            g.view_route_name = 'employee.read'
        if self.request.has_perm('employees.update'):
            g.editable = True
            g.edit_route_name = 'employee.update'
        if self.request.has_perm('employees.delete'):
            g.deletable = True
            g.delete_route_name = 'employee.delete'

        return g


class EmployeeCrud(CrudView):

    mapped_class = Employee
    home_route = 'employees'

    def fieldset(self, model):
        fs = self.make_fieldset(model)
        fs.append(AssociationProxyField('first_name'))
        fs.append(AssociationProxyField('last_name'))
        fs.append(AssociationProxyField('display_name'))
        fs.configure(
            include=[
                fs.id.label("ID"),
                fs.first_name,
                fs.last_name,
                fs.phone.label("Phone Number").readonly(),
                fs.email.label("Email Address").readonly(),
                fs.status.with_renderer(EnumFieldRenderer(EMPLOYEE_STATUS)),
                ])
        return fs


def add_routes(config):
    config.add_route('employees',       '/employees')
    config.add_route('employee.create', '/employees/new')
    config.add_route('employee.read',   '/employees/{uuid}')
    config.add_route('employee.update', '/employees/{uuid}/edit')
    config.add_route('employee.delete', '/employees/{uuid}/delete')


def includeme(config):
    add_routes(config)

    config.add_view(EmployeesGrid, route_name='employees',
                    renderer='/employees/index.mako',
                    permission='employees.list')
    config.add_view(EmployeeCrud, attr='create', route_name='employee.create',
                    renderer='/employees/crud.mako',
                    permission='employees.create')
    config.add_view(EmployeeCrud, attr='read', route_name='employee.read',
                    renderer='/employees/crud.mako',
                    permission='employees.read')
    config.add_view(EmployeeCrud, attr='update', route_name='employee.update',
                    renderer='/employees/crud.mako',
                    permission='employees.update')
    config.add_view(EmployeeCrud, attr='delete', route_name='employee.delete',
                    permission='employees.delete')
