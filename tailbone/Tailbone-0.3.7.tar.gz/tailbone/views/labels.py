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
Label Views
"""

from pyramid.httpexceptions import HTTPFound

import formalchemy

from webhelpers.html import HTML

from ..db import Session
from . import SearchableAlchemyGridView, CrudView
from ..grids.search import BooleanSearchFilter
from edbob.pyramid.forms import StrippingFieldRenderer

from rattail.db.model import LabelProfile


class ProfilesGrid(SearchableAlchemyGridView):

    mapped_class = LabelProfile
    config_prefix = 'label_profiles'
    sort = 'ordinal'

    def filter_map(self):
        return self.make_filter_map(
            exact=['code', 'visible'],
            ilike=['description'])

    def filter_config(self):
        return self.make_filter_config(
            filter_factory_visible=BooleanSearchFilter)

    def sort_map(self):
        return self.make_sort_map('ordinal', 'code', 'description', 'visible')

    def grid(self):
        g = self.make_grid()
        g.configure(
            include=[
                g.ordinal,
                g.code,
                g.description,
                g.visible,
                ],
            readonly=True)
        if self.request.has_perm('label_profiles.read'):
            g.viewable = True
            g.view_route_name = 'label_profile.read'
        if self.request.has_perm('label_profiles.update'):
            g.editable = True
            g.edit_route_name = 'label_profile.update'
        if self.request.has_perm('label_profiles.delete'):
            g.deletable = True
            g.delete_route_name = 'label_profile.delete'
        return g


class ProfileCrud(CrudView):

    mapped_class = LabelProfile
    home_route = 'label_profiles'
    pretty_name = "Label Profile"
    update_cancel_route = 'label_profile.read'

    def fieldset(self, model):

        class FormatFieldRenderer(formalchemy.TextAreaFieldRenderer):

            def render_readonly(self, **kwargs):
                value = self.raw_value
                if not value:
                    return ''
                return HTML.tag('pre', c=value)

            def render(self, **kwargs):
                kwargs.setdefault('size', (80, 8))
                return super(FormatFieldRenderer, self).render(**kwargs)

        fs = self.make_fieldset(model)
        fs.printer_spec.set(renderer=StrippingFieldRenderer)
        fs.formatter_spec.set(renderer=StrippingFieldRenderer)
        fs.format.set(renderer=FormatFieldRenderer)
        fs.configure(
            include=[
                fs.ordinal,
                fs.code,
                fs.description,
                fs.printer_spec,
                fs.formatter_spec,
                fs.format,
                fs.visible,
                ])
        return fs

    def post_save(self, form):
        profile = form.fieldset.model
        if not profile.format:
            formatter = profile.get_formatter()
            if formatter:
                try:
                    profile.format = formatter.default_format
                except NotImplementedError:
                    pass

    def post_save_url(self, form):
        return self.request.route_url('label_profile.read',
                                      uuid=form.fieldset.model.uuid)


def printer_settings(request):
    uuid = request.matchdict['uuid']
    profile = Session.query(LabelProfile).get(uuid) if uuid else None
    if not profile:
        return HTTPFound(location=request.route_url('label_profiles'))

    read_profile = HTTPFound(location=request.route_url(
            'label_profile.read', uuid=profile.uuid))

    printer = profile.get_printer()
    if not printer:
        request.session.flash("Label profile \"%s\" does not have a functional "
                              "printer spec." % profile)
        return read_profile
    if not printer.required_settings:
        request.session.flash("Printer class for label profile \"%s\" does not "
                              "require any settings." % profile)
        return read_profile

    if request.POST:
        for setting in printer.required_settings:
            if setting in request.POST:
                profile.save_printer_setting(setting, request.POST[setting])
        return read_profile

    return {'profile': profile, 'printer': printer}


def includeme(config):

    config.add_route('label_profiles', '/labels/profiles')
    config.add_view(ProfilesGrid, route_name='label_profiles',
                    renderer='/labels/profiles/index.mako',
                    permission='label_profiles.list')

    config.add_route('label_profile.create', '/labels/profiles/new')
    config.add_view(ProfileCrud, attr='create', route_name='label_profile.create',
                    renderer='/labels/profiles/crud.mako',
                    permission='label_profiles.create')

    config.add_route('label_profile.read', '/labels/profiles/{uuid}')
    config.add_view(ProfileCrud, attr='read', route_name='label_profile.read',
                    renderer='/labels/profiles/read.mako',
                    permission='label_profiles.read')

    config.add_route('label_profile.update', '/labels/profiles/{uuid}/edit')
    config.add_view(ProfileCrud, attr='update', route_name='label_profile.update',
                    renderer='/labels/profiles/crud.mako',
                    permission='label_profiles.update')

    config.add_route('label_profile.delete', '/labels/profiles/{uuid}/delete')
    config.add_view(ProfileCrud, attr='delete', route_name='label_profile.delete',
                    permission='label_profiles.delete')

    config.add_route('label_profile.printer_settings', '/labels/profiles/{uuid}/printer')
    config.add_view(printer_settings, route_name='label_profile.printer_settings',
                    renderer='/labels/profiles/printer.mako',
                    permission='label_profiles.update')
