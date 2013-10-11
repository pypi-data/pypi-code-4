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
``pyramid_simpleform`` Forms
"""

from pyramid_simpleform import renderers

from webhelpers.html import tags
from webhelpers.html import HTML

from edbob.util import prettify


__all__ = ['FormRenderer']


class FormRenderer(renderers.FormRenderer):
    """
    Customized form renderer.  Provides some extra methods for convenience.
    """

    def field_div(self, name, field, label=None):
        errors = self.errors_for(name)
        if errors:
            errors = [HTML.tag('div', class_='field-error', c=x) for x in errors]
            errors = tags.literal('').join(errors)

        label = HTML.tag('label', for_=name, c=label or prettify(name))
        inner = HTML.tag('div', class_='field', c=field)

        outer_class = 'field-wrapper'
        if errors:
            outer_class += ' error'
        outer = HTML.tag('div', class_=outer_class, c=(errors or '') + label + inner)
        return outer

    def referrer_field(self):
        return self.hidden('referrer', value=self.form.request.get_referrer())
