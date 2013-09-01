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
Core Batch Views
"""

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response

from webhelpers.html import tags

from edbob.pyramid.forms import PrettyDateTimeFieldRenderer
from ...forms import EnumFieldRenderer
from ...grids.search import BooleanSearchFilter
from edbob.pyramid.progress import SessionProgress
from .. import SearchableAlchemyGridView, CrudView, View

import rattail
from rattail import batches
from ... import Session
from rattail.db.model import Batch
from rattail.threads import Thread


class BatchesGrid(SearchableAlchemyGridView):

    mapped_class = Batch
    config_prefix = 'batches'
    sort = 'id'

    def filter_map(self):

        def executed_is(q, v):
            if v == 'True':
                return q.filter(Batch.executed != None)
            else:
                return q.filter(Batch.executed == None)

        def executed_isnot(q, v):
            if v == 'True':
                return q.filter(Batch.executed == None)
            else:
                return q.filter(Batch.executed != None)

        return self.make_filter_map(
            exact=['id'],
            ilike=['source', 'destination', 'description'],
            executed={
                'is': executed_is,
                'nt': executed_isnot,
                })

    def filter_config(self):
        return self.make_filter_config(
            filter_label_id="ID",
            filter_factory_executed=BooleanSearchFilter,
            include_filter_executed=True,
            filter_type_executed='is',
            executed='False')

    def sort_map(self):
        return self.make_sort_map('source', 'id', 'destination', 'description', 'executed')

    def grid(self):
        g = self.make_grid()
        g.executed.set(renderer=PrettyDateTimeFieldRenderer(from_='utc'))
        g.configure(
            include=[
                g.source,
                g.id.label("ID"),
                g.destination,
                g.description,
                g.rowcount.label("Row Count"),
                g.executed,
                ],
            readonly=True)
        if self.request.has_perm('batches.read'):
            def rows(row):
                return tags.link_to("View Rows", self.request.route_url(
                        'batch.rows', uuid=row.uuid))
            g.add_column('rows', "", rows)
            g.viewable = True
            g.view_route_name = 'batch.read'
        if self.request.has_perm('batches.update'):
            g.editable = True
            g.edit_route_name = 'batch.update'
        if self.request.has_perm('batches.delete'):
            g.deletable = True
            g.delete_route_name = 'batch.delete'
        return g


class BatchCrud(CrudView):

    mapped_class = Batch
    home_route = 'batches'

    def fieldset(self, model):
        fs = self.make_fieldset(model)
        fs.action_type.set(renderer=EnumFieldRenderer(rattail.BATCH_ACTION))
        fs.executed.set(renderer=PrettyDateTimeFieldRenderer(from_='utc'))
        fs.configure(
            include=[
                fs.source,
                fs.id.label("ID"),
                fs.destination,
                fs.action_type,
                fs.description,
                fs.rowcount.label("Row Count").readonly(),
                fs.executed.readonly(),
                ])
        return fs

    def post_delete(self, batch):
        batch.drop_table()


class ExecuteBatch(View):

    def execute_batch(self, batch, progress):
        from rattail.db import Session
        session = Session()
        batch = session.merge(batch)

        if not batch.execute(progress):
            session.rollback()
            session.close()
            return

        session.commit()
        session.refresh(batch)
        session.close()

        progress.session.load()
        progress.session['complete'] = True
        progress.session['success_msg'] = "Batch \"%s\" has been executed." % batch.description
        progress.session['success_url'] = self.request.route_url('batches')
        progress.session.save()        

    def __call__(self):
        uuid = self.request.matchdict['uuid']
        batch = Session.query(Batch).get(uuid) if uuid else None
        if not batch:
            return HTTPFound(location=self.request.route_url('batches'))

        progress = SessionProgress(self.request.session, 'batch.execute')
        thread = Thread(target=self.execute_batch, args=(batch, progress))
        thread.start()
        kwargs = {
            'key': 'batch.execute',
            'cancel_url': self.request.route_url('batch.rows', uuid=batch.uuid),
            'cancel_msg': "Batch execution was canceled.",
            }
        return render_to_response('/progress.mako', kwargs, request=self.request)


def includeme(config):

    config.add_route('batches', '/batches')
    config.add_view(BatchesGrid, route_name='batches',
                    renderer='/batches/index.mako',
                    permission='batches.list')

    config.add_route('batch.read', '/batches/{uuid}')
    config.add_view(BatchCrud, attr='read',
                    route_name='batch.read',
                    renderer='/batches/read.mako',
                    permission='batches.read')

    config.add_route('batch.update', '/batches/{uuid}/edit')
    config.add_view(BatchCrud, attr='update', route_name='batch.update',
                    renderer='/batches/crud.mako',
                    permission='batches.update')

    config.add_route('batch.delete', '/batches/{uuid}/delete')
    config.add_view(BatchCrud, attr='delete', route_name='batch.delete',
                    permission='batches.delete')

    config.add_route('batch.execute', '/batches/{uuid}/execute')
    config.add_view(ExecuteBatch, route_name='batch.execute',
                    permission='batches.execute')
