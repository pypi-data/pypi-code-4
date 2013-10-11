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
Vendor Views
"""

from . import SearchableAlchemyGridView, CrudView, AutocompleteView
from ..forms import AssociationProxyField, PersonFieldRenderer
from rattail.db.model import Vendor


class VendorsGrid(SearchableAlchemyGridView):

    mapped_class = Vendor
    config_prefix = 'vendors'
    sort = 'name'

    def filter_map(self):
        return self.make_filter_map(exact=['id'], ilike=['name'])

    def filter_config(self):
        return self.make_filter_config(
            include_filter_name=True,
            filter_type_name='lk',
            filter_label_id="ID")

    def sort_map(self):
        return self.make_sort_map('id', 'name')

    def grid(self):
        g = self.make_grid()
        g.append(AssociationProxyField('contact'))
        g.configure(
            include=[
                g.id.label("ID"),
                g.name,
                g.phone.label("Phone Number"),
                g.email.label("Email Address"),
                g.contact,
                ],
            readonly=True)
        if self.request.has_perm('vendors.read'):
            g.viewable = True
            g.view_route_name = 'vendor.read'
        if self.request.has_perm('vendors.update'):
            g.editable = True
            g.edit_route_name = 'vendor.update'
        if self.request.has_perm('vendors.delete'):
            g.deletable = True
            g.delete_route_name = 'vendor.delete'
        return g


class VendorCrud(CrudView):

    mapped_class = Vendor
    home_route = 'vendors'

    def fieldset(self, model):
        fs = self.make_fieldset(model)
        fs.append(AssociationProxyField('contact'))
        fs.configure(
            include=[
                fs.id.label("ID"),
                fs.name,
                fs.special_discount,
                fs.phone.label("Phone Number").readonly(),
                fs.email.label("Email Address").readonly(),
                fs.contact.with_renderer(PersonFieldRenderer).readonly(),
                ])
        return fs


class VendorsAutocomplete(AutocompleteView):

    mapped_class = Vendor
    fieldname = 'name'


def add_routes(config):
    config.add_route('vendors', '/vendors')
    config.add_route('vendors.autocomplete', '/vendors/autocomplete')
    config.add_route('vendor.create', '/vendors/new')
    config.add_route('vendor.read', '/vendors/{uuid}')
    config.add_route('vendor.update', '/vendors/{uuid}/edit')
    config.add_route('vendor.delete', '/vendors/{uuid}/delete')


def includeme(config):
    add_routes(config)

    config.add_view(VendorsGrid, route_name='vendors',
                    renderer='/vendors/index.mako',
                    permission='vendors.list')
    config.add_view(VendorsAutocomplete, route_name='vendors.autocomplete',
                    renderer='json', permission='vendors.list')
    config.add_view(VendorCrud, attr='create', route_name='vendor.create',
                    renderer='/vendors/crud.mako',
                    permission='vendors.create')
    config.add_view(VendorCrud, attr='read', route_name='vendor.read',
                    renderer='/vendors/crud.mako',
                    permission='vendors.read')
    config.add_view(VendorCrud, attr='update', route_name='vendor.update',
                    renderer='/vendors/crud.mako',
                    permission='vendors.update')
    config.add_view(VendorCrud, attr='delete', route_name='vendor.delete',
                    permission='vendors.delete')
