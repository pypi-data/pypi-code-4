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
FormAlchemy Field Renderers
"""

from webhelpers.html import literal
from webhelpers.html import tags

import formalchemy

from edbob.pyramid.forms import pretty_datetime
from edbob.pyramid.forms.formalchemy.renderers import YesNoFieldRenderer

from .common import AutocompleteFieldRenderer, EnumFieldRenderer
from .products import GPCFieldRenderer, ProductFieldRenderer
from .users import UserFieldRenderer


__all__ = ['AutocompleteFieldRenderer', 'EnumFieldRenderer', 'YesNoFieldRenderer',
           'GPCFieldRenderer', 'PersonFieldRenderer', 'PriceFieldRenderer',
           'PriceWithExpirationFieldRenderer', 'ProductFieldRenderer', 'UserFieldRenderer']


def PersonFieldRenderer(url):

    BaseRenderer = AutocompleteFieldRenderer(url)

    class PersonFieldRenderer(BaseRenderer):

        def render_readonly(self, **kwargs):
            person = self.raw_value
            if not person:
                return ''
            return tags.link_to(
                str(person),
                self.request.route_url('person.read', uuid=person.uuid))

    return PersonFieldRenderer


class PriceFieldRenderer(formalchemy.TextFieldRenderer):
    """
    Renderer for fields which reference a :class:`ProductPrice` instance.
    """

    def render_readonly(self, **kwargs):
        price = self.field.raw_value
        if price:
            if price.price is not None and price.pack_price is not None:
                if price.multiple > 1:
                    return literal('$ %0.2f / %u&nbsp; ($ %0.2f / %u)' % (
                            price.price, price.multiple,
                            price.pack_price, price.pack_multiple))
                return literal('$ %0.2f&nbsp; ($ %0.2f / %u)' % (
                        price.price, price.pack_price, price.pack_multiple))
            if price.price is not None:
                if price.multiple > 1:
                    return '$ %0.2f / %u' % (price.price, price.multiple)
                return '$ %0.2f' % price.price
            if price.pack_price is not None:
                return '$ %0.2f / %u' % (price.pack_price, price.pack_multiple)
        return ''


class PriceWithExpirationFieldRenderer(PriceFieldRenderer):
    """
    Price field renderer which also displays the expiration date, if present.
    """

    def render_readonly(self, **kwargs):
        res = super(PriceWithExpirationFieldRenderer, self).render_readonly(**kwargs)
        if res:
            price = self.field.raw_value
            if price.ends:
                res += '&nbsp; (%s)' % pretty_datetime(price.ends, from_='utc')
        return res
