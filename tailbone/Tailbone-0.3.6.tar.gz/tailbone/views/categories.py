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
Category Views
"""

from . import SearchableAlchemyGridView, CrudView

from rattail.db.model import Category


class CategoriesGrid(SearchableAlchemyGridView):

    mapped_class = Category
    config_prefix = 'categories'
    sort = 'number'

    def filter_map(self):
        return self.make_filter_map(exact=['number'], ilike=['name'])

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
        if self.request.has_perm('categories.read'):
            g.viewable = True
            g.view_route_name = 'category.read'
        if self.request.has_perm('categories.update'):
            g.editable = True
            g.edit_route_name = 'category.update'
        if self.request.has_perm('categories.delete'):
            g.deletable = True
            g.delete_route_name = 'category.delete'
        return g


class CategoryCrud(CrudView):

    mapped_class = Category
    home_route = 'categories'

    def fieldset(self, model):
        fs = self.make_fieldset(model)
        fs.configure(
            include=[
                fs.number,
                fs.name,
                ])
        return fs


def includeme(config):

    config.add_route('categories', '/categories')
    config.add_view(CategoriesGrid, route_name='categories',
                    renderer='/categories/index.mako',
                    permission='categories.list')

    config.add_route('category.create', '/categories/new')
    config.add_view(CategoryCrud, attr='create', route_name='category.create',
                    renderer='/categories/crud.mako',
                    permission='categories.create')

    config.add_route('category.read', '/categories/{uuid}')
    config.add_view(CategoryCrud, attr='read', route_name='category.read',
                    renderer='/categories/crud.mako',
                    permission='categories.read')

    config.add_route('category.update', '/categories/{uuid}/edit')
    config.add_view(CategoryCrud, attr='update', route_name='category.update',
                    renderer='/categories/crud.mako',
                    permission='categories.update')

    config.add_route('category.delete', '/categories/{uuid}/delete')
    config.add_view(CategoryCrud, attr='delete', route_name='category.delete',
                    permission='categories.delete')
