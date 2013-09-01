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
Customer Views
"""

from sqlalchemy import and_

from edbob.enum import EMAIL_PREFERENCE

from . import SearchableAlchemyGridView
from ..forms import EnumFieldRenderer

import rattail
from .. import Session
from rattail.db.model import (
    Customer, CustomerPerson, CustomerGroupAssignment,
    CustomerEmailAddress, CustomerPhoneNumber)
from . import CrudView


class CustomersGrid(SearchableAlchemyGridView):

    mapped_class = Customer
    config_prefix = 'customers'
    sort = 'name'

    def join_map(self):
        return {
            'email':
                lambda q: q.outerjoin(CustomerEmailAddress, and_(
                    CustomerEmailAddress.parent_uuid == Customer.uuid,
                    CustomerEmailAddress.preference == 1)),
            'phone':
                lambda q: q.outerjoin(CustomerPhoneNumber, and_(
                    CustomerPhoneNumber.parent_uuid == Customer.uuid,
                    CustomerPhoneNumber.preference == 1)),
            }

    def filter_map(self):
        return self.make_filter_map(
            exact=['id'],
            ilike=['name'],
            email=self.filter_ilike(CustomerEmailAddress.address),
            phone=self.filter_ilike(CustomerPhoneNumber.number))

    def filter_config(self):
        return self.make_filter_config(
            include_filter_name=True,
            filter_type_name='lk',
            filter_label_phone="Phone Number",
            filter_label_email="Email Address",
            filter_label_id="ID")

    def sort_map(self):
        return self.make_sort_map(
            'id', 'name',
            email=self.sorter(CustomerEmailAddress.address),
            phone=self.sorter(CustomerPhoneNumber.number))

    def grid(self):
        g = self.make_grid()
        g.configure(
            include=[
                g.id.label("ID"),
                g.name,
                g.phone.label("Phone Number"),
                g.email.label("Email Address"),
                ],
            readonly=True)

        if self.request.has_perm('customers.read'):
            g.viewable = True
            g.view_route_name = 'customer.read'
        if self.request.has_perm('customers.update'):
            g.editable = True
            g.edit_route_name = 'customer.update'
        if self.request.has_perm('customers.delete'):
            g.deletable = True
            g.delete_route_name = 'customer.delete'

        return g


class CustomerCrud(CrudView):

    mapped_class = Customer
    home_route = 'customers'

    def get_model(self, key):
        model = super(CustomerCrud, self).get_model(key)
        if model:
            return model
        model = Session.query(Customer).filter_by(id=key).first()
        if model:
            return model
        model = Session.query(CustomerPerson).get(key)
        if model:
            return model.customer
        model = Session.query(CustomerGroupAssignment).get(key)
        if model:
            return model.customer
        return None

    def fieldset(self, model):
        fs = self.make_fieldset(model)
        fs.email_preference.set(renderer=EnumFieldRenderer(EMAIL_PREFERENCE))
        fs.configure(
            include=[
                fs.id.label("ID"),
                fs.name,
                fs.phone.label("Phone Number").readonly(),
                fs.email.label("Email Address").readonly(),
                fs.email_preference,
                ])
        return fs


def add_routes(config):
    config.add_route('customers',       '/customers')
    config.add_route('customer.create', '/customers/new')
    config.add_route('customer.read',   '/customers/{uuid}')
    config.add_route('customer.update', '/customers/{uuid}/edit')
    config.add_route('customer.delete', '/customers/{uuid}/delete')


def includeme(config):
    add_routes(config)

    config.add_view(CustomersGrid, route_name='customers',
                    renderer='/customers/index.mako',
                    permission='customers.list')
    config.add_view(CustomerCrud, attr='create', route_name='customer.create',
                    renderer='/customers/crud.mako',
                    permission='customers.create')
    config.add_view(CustomerCrud, attr='read', route_name='customer.read',
                    renderer='/customers/read.mako',
                    permission='customers.read')
    config.add_view(CustomerCrud, attr='update', route_name='customer.update',
                    renderer='/customers/crud.mako',
                    permission='customers.update')
    config.add_view(CustomerCrud, attr='delete', route_name='customer.delete',
                    permission='customers.delete')
