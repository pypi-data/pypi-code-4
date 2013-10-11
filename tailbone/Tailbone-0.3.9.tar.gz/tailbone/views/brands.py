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
Brand Views
"""

from . import SearchableAlchemyGridView, CrudView, AutocompleteView

from rattail.db.model import Brand


class BrandsGrid(SearchableAlchemyGridView):

    mapped_class = Brand
    config_prefix = 'brands'
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
        if self.request.has_perm('brands.read'):
            g.viewable = True
            g.view_route_name = 'brand.read'
        if self.request.has_perm('brands.update'):
            g.editable = True
            g.edit_route_name = 'brand.update'
        if self.request.has_perm('brands.delete'):
            g.deletable = True
            g.delete_route_name = 'brand.delete'
        return g


class BrandCrud(CrudView):

    mapped_class = Brand
    home_route = 'brands'

    def fieldset(self, model):
        fs = self.make_fieldset(model)
        fs.configure(
            include=[
                fs.name,
                ])
        return fs


class BrandsAutocomplete(AutocompleteView):

    mapped_class = Brand
    fieldname = 'name'


def add_routes(config):
    config.add_route('brands', '/brands')
    config.add_route('brands.autocomplete', '/brands/autocomplete')
    config.add_route('brand.create', '/brands/new')
    config.add_route('brand.read', '/brands/{uuid}')
    config.add_route('brand.update', '/brands/{uuid}/edit')
    config.add_route('brand.delete', '/brands/{uuid}/delete')


def includeme(config):
    add_routes(config)

    config.add_view(BrandsGrid,
                    route_name='brands',
                    renderer='/brands/index.mako',
                    permission='brands.list')
    config.add_view(BrandsAutocomplete,
                    route_name='brands.autocomplete',
                    renderer='json',
                    permission='brands.list')
    config.add_view(BrandCrud, attr='create',
                    route_name='brand.create',
                    renderer='/brands/crud.mako',
                    permission='brands.create')
    config.add_view(BrandCrud, attr='read',
                    route_name='brand.read',
                    renderer='/brands/crud.mako',
                    permission='brands.read')
    config.add_view(BrandCrud, attr='update',
                    route_name='brand.update',
                    renderer='/brands/crud.mako',
                    permission='brands.update')
    config.add_view(BrandCrud, attr='delete',
                    route_name='brand.delete',
                    permission='brands.delete')
