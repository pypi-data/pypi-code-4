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
Batch Row Views
"""

from .. import SearchableAlchemyGridView, CrudView
from pyramid.httpexceptions import HTTPFound

from ...db import Session
from rattail.db.model import Batch, LabelProfile
from ...forms import GPCFieldRenderer


def field_with_renderer(field, column):

    if column.sil_name == 'F01': # UPC
        field = field.with_renderer(GPCFieldRenderer)

    elif column.sil_name == 'F95': # Shelf Tag Type
        q = Session.query(LabelProfile)
        q = q.order_by(LabelProfile.ordinal)
        field = field.dropdown(options=[(x.description, x.code) for x in q])

    return field


def BatchRowsGrid(request):
    uuid = request.matchdict['uuid']
    batch = Session.query(Batch).get(uuid) if uuid else None
    if not batch:
        return HTTPFound(location=request.route_url('batches'))

    class BatchRowsGrid(SearchableAlchemyGridView):

        mapped_class = batch.rowclass
        config_prefix = 'batch.%s' % batch.uuid
        sort = 'ordinal'

        def filter_map(self):
            fmap = self.make_filter_map()
            for column in batch.columns:
                if column.visible:
                    if column.data_type.startswith('CHAR'):
                        fmap[column.name] = self.filter_ilike(
                            getattr(batch.rowclass, column.name))
                    else:
                        fmap[column.name] = self.filter_exact(
                            getattr(batch.rowclass, column.name))
            return fmap

        def filter_config(self):
            config = self.make_filter_config()
            for column in batch.columns:
                if column.visible:
                    config['filter_label_%s' % column.name] = column.display_name
            return config

        def grid(self):
            g = self.make_grid()

            include = [g.ordinal.label("Row")]
            for column in batch.columns:
                if column.visible:
                    field = getattr(g, column.name)
                    field = field_with_renderer(field, column)
                    field = field.label(column.display_name)
                    include.append(field)
                    g.column_titles[field.key] = '%s - %s - %s' % (
                        column.sil_name, column.description, column.data_type)

            g.configure(include=include, readonly=True)

            route_kwargs = lambda x: {'batch_uuid': x.batch.uuid, 'uuid': x.uuid}

            if self.request.has_perm('batch_rows.read'):
                g.viewable = True
                g.view_route_name = 'batch_row.read'
                g.view_route_kwargs = route_kwargs

            if self.request.has_perm('batch_rows.update'):
                g.editable = True
                g.edit_route_name = 'batch_row.update'
                g.edit_route_kwargs = route_kwargs

            if self.request.has_perm('batch_rows.delete'):
                g.deletable = True
                g.delete_route_name = 'batch_row.delete'
                g.delete_route_kwargs = route_kwargs

            return g

        def render_kwargs(self):
            return {'batch': batch}

    grid = BatchRowsGrid(request)
    grid.batch = batch
    return grid


def batch_rows_grid(request):
    result = BatchRowsGrid(request)
    if isinstance(result, HTTPFound):
        return result
    return result()


def batch_rows_delete(request):
    grid = BatchRowsGrid(request)
    grid._filter_config = grid.filter_config()
    rows = grid.make_query()
    count = rows.count()
    rows.delete(synchronize_session=False)
    grid.batch.rowcount -= count
    request.session.flash("Deleted %d rows from batch." % count)
    return HTTPFound(location=request.route_url('batch.rows', uuid=grid.batch.uuid))


def batch_row_crud(request, attr):
    batch_uuid = request.matchdict['batch_uuid']
    batch = Session.query(Batch).get(batch_uuid)
    if not batch:
        return HTTPFound(location=request.route_url('batches'))

    row_uuid = request.matchdict['uuid']
    row = Session.query(batch.rowclass).get(row_uuid)
    if not row:
        return HTTPFound(location=request.route_url('batch.read', uuid=batch.uuid))

    class BatchRowCrud(CrudView):

        mapped_class = batch.rowclass
        pretty_name = "Batch Row"

        @property
        def home_url(self):
            return self.request.route_url('batch.rows', uuid=batch.uuid)

        @property
        def cancel_url(self):
            return self.home_url

        def fieldset(self, model):
            fs = self.make_fieldset(model)

            include = [fs.ordinal.label("Row Number").readonly()]
            for column in batch.columns:
                field = getattr(fs, column.name)
                field = field_with_renderer(field, column)
                field = field.label(column.display_name)
                include.append(field)

            fs.configure(include=include)
            return fs

        def flash_delete(self, row):
            self.request.session.flash("Batch Row %d has been deleted."
                                       % row.ordinal)

        def post_delete(self, model):
            batch.rowcount -= 1

    crud = BatchRowCrud(request)
    return getattr(crud, attr)()

def batch_row_read(request):
    return batch_row_crud(request, 'read')

def batch_row_update(request):
    return batch_row_crud(request, 'update')

def batch_row_delete(request):
    return batch_row_crud(request, 'delete')


def includeme(config):

    config.add_route('batch.rows', '/batches/{uuid}/rows')
    config.add_view(batch_rows_grid, route_name='batch.rows',
                    renderer='/batches/rows/index.mako',
                    permission='batches.read')

    config.add_route('batch.rows.delete', '/batches/{uuid}/rows/delete')
    config.add_view(batch_rows_delete, route_name='batch.rows.delete',
                    permission='batch_rows.delete')

    config.add_route('batch_row.read', '/batches/{batch_uuid}/{uuid}')
    config.add_view(batch_row_read, route_name='batch_row.read',
                    renderer='/batches/rows/crud.mako',
                    permission='batch_rows.read')

    config.add_route('batch_row.update', '/batches/{batch_uuid}/{uuid}/edit')
    config.add_view(batch_row_update, route_name='batch_row.update',
                    renderer='/batches/rows/crud.mako',
                    permission='batch_rows.update')

    config.add_route('batch_row.delete', '/batches/{batch_uuid}/{uuid}/delete')
    config.add_view(batch_row_delete, route_name='batch_row.delete',
                    permission='batch_rows.delete')
