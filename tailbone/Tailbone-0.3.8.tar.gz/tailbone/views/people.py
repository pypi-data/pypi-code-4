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
Person Views
"""

from sqlalchemy import and_

from . import SearchableAlchemyGridView, CrudView, AutocompleteView

from ..db import Session
from rattail.db.model import (Person, PersonEmailAddress, PersonPhoneNumber,
                              VendorContact)


class PeopleGrid(SearchableAlchemyGridView):

    mapped_class = Person
    config_prefix = 'people'
    sort = 'first_name'

    def join_map(self):
        return {
            'email':
                lambda q: q.outerjoin(PersonEmailAddress, and_(
                    PersonEmailAddress.parent_uuid == Person.uuid,
                    PersonEmailAddress.preference == 1)),
            'phone':
                lambda q: q.outerjoin(PersonPhoneNumber, and_(
                    PersonPhoneNumber.parent_uuid == Person.uuid,
                    PersonPhoneNumber.preference == 1)),
            }

    def filter_map(self):
        return self.make_filter_map(
            ilike=['first_name', 'last_name', 'display_name'],
            email=self.filter_ilike(PersonEmailAddress.address),
            phone=self.filter_ilike(PersonPhoneNumber.number))

    def filter_config(self):
        return self.make_filter_config(
            include_filter_first_name=True,
            filter_type_first_name='lk',
            include_filter_last_name=True,
            filter_type_last_name='lk',
            filter_label_phone="Phone Number",
            filter_label_email="Email Address")

    def sort_map(self):
        return self.make_sort_map(
            'first_name', 'last_name', 'display_name',
            email=self.sorter(PersonEmailAddress.address),
            phone=self.sorter(PersonPhoneNumber.number))

    def grid(self):
        g = self.make_grid()
        g.configure(
            include=[
                g.first_name,
                g.last_name,
                g.display_name,
                g.phone.label("Phone Number"),
                g.email.label("Email Address"),
                ],
            readonly=True)

        if self.request.has_perm('people.read'):
            g.viewable = True
            g.view_route_name = 'person.read'
        if self.request.has_perm('people.update'):
            g.editable = True
            g.edit_route_name = 'person.update'
        # if self.request.has_perm('products.delete'):
        #     g.deletable = True
        #     g.delete_route_name = 'product.delete'

        return g


class PersonCrud(CrudView):

    mapped_class = Person
    home_route = 'people'

    def get_model(self, key):
        model = super(PersonCrud, self).get_model(key)
        if model:
            return model
        model = Session.query(VendorContact).get(key)
        if model:
            return model.person
        return None

    def fieldset(self, model):
        fs = self.make_fieldset(model)
        fs.configure(
            include=[
                fs.first_name,
                fs.last_name,
                fs.display_name,
                fs.phone.label("Phone Number").readonly(),
                fs.email.label("Email Address").readonly(),
                ])
        return fs


class PeopleAutocomplete(AutocompleteView):

    mapped_class = Person
    fieldname = 'display_name'


def add_routes(config):
    config.add_route('people',                  '/people')
    config.add_route('people.autocomplete',     '/people/autocomplete')
    config.add_route('person.read',             '/people/{uuid}')
    config.add_route('person.update',           '/people/{uuid}/edit')


def includeme(config):
    add_routes(config)

    config.add_view(PeopleGrid, route_name='people',
                    renderer='/people/index.mako',
                    permission='people.list')
    config.add_view(PersonCrud, attr='read', route_name='person.read',
                    renderer='/people/crud.mako',
                    permission='people.read')
    config.add_view(PersonCrud, attr='update', route_name='person.update',
                    renderer='/people/crud.mako',
                    permission='people.update')
    config.add_view(PeopleAutocomplete, route_name='people.autocomplete',
                    renderer='json',
                    permission='people.list')
