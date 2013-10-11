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
Autocomplete View
"""

from .core import View
from ..db import Session


__all__ = ['AutocompleteView']


class AutocompleteView(View):

    def filter_query(self, q):
        return q

    def make_query(self, term):
        q = Session.query(self.mapped_class)
        q = self.filter_query(q)
        q = q.filter(getattr(self.mapped_class, self.fieldname).ilike('%%%s%%' % term))
        q = q.order_by(getattr(self.mapped_class, self.fieldname))
        return q

    def query(self, term):
        return self.make_query(term)

    def display(self, instance):
        return getattr(instance, self.fieldname)

    def __call__(self):
        term = self.request.params.get('term')
        if term:
            term = term.strip()
        if not term:
            return []
        results = self.query(term).all()
        return [{'label': self.display(x), 'value': x.uuid} for x in results]
