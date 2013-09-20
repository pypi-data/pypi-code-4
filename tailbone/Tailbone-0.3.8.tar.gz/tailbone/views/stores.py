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
Store Views
"""

from sqlalchemy import and_

from . import SearchableAlchemyGridView, CrudView
from rattail.db.model import Store, StoreEmailAddress, StorePhoneNumber


class StoresGrid(SearchableAlchemyGridView):

    mapped_class = Store
    config_prefix = 'stores'
    sort = 'id'

    def join_map(self):
        return {
            'email':
                lambda q: q.outerjoin(StoreEmailAddress, and_(
                    StoreEmailAddress.parent_uuid == Store.uuid,
                    StoreEmailAddress.preference == 1)),
            'phone':
                lambda q: q.outerjoin(StorePhoneNumber, and_(
                    StorePhoneNumber.parent_uuid == Store.uuid,
                    StorePhoneNumber.preference == 1)),
            }

    def filter_map(self):
        return self.make_filter_map(
            exact=['id'],
            ilike=['name'],
            email=self.filter_ilike(StoreEmailAddress.address),
            phone=self.filter_ilike(StorePhoneNumber.number))

    def filter_config(self):
        return self.make_filter_config(
            include_filter_name=True,
            filter_type_name='lk',
            filter_label_id="ID")

    def sort_map(self):
        return self.make_sort_map(
            'id', 'name',
            email=self.sorter(StoreEmailAddress.address),
            phone=self.sorter(StorePhoneNumber.number))

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
        g.viewable = True
        g.view_route_name = 'store.read'
        if self.request.has_perm('stores.update'):
            g.editable = True
            g.edit_route_name = 'store.update'
        if self.request.has_perm('stores.delete'):
            g.deletable = True
            g.delete_route_name = 'store.delete'
        return g


class StoreCrud(CrudView):

    mapped_class = Store
    home_route = 'stores'

    def fieldset(self, model):
        fs = self.make_fieldset(model)
        fs.configure(
            include=[
                fs.id.label("ID"),
                fs.name,
                fs.phone.label("Phone Number").readonly(),
                fs.email.label("Email Address").readonly(),
                ])
        return fs


def includeme(config):

    config.add_route('stores', '/stores')
    config.add_view(StoresGrid, route_name='stores',
                    renderer='/stores/index.mako',
                    permission='stores.list')

    config.add_route('store.create', '/stores/new')
    config.add_view(StoreCrud, attr='create', route_name='store.create',
                    renderer='/stores/crud.mako',
                    permission='stores.create')

    config.add_route('store.read', '/stores/{uuid}')
    config.add_view(StoreCrud, attr='read', route_name='store.read',
                    renderer='/stores/crud.mako',
                    permission='stores.read')

    config.add_route('store.update', '/stores/{uuid}/edit')
    config.add_view(StoreCrud, attr='update', route_name='store.update',
                    renderer='/stores/crud.mako',
                    permission='stores.update')

    config.add_route('store.delete', '/stores/{uuid}/delete')
    config.add_view(StoreCrud, attr='delete', route_name='store.delete',
                    permission='stores.delete')
