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
Product Field Renderers
"""

from formalchemy import TextFieldRenderer
from rattail.gpc import GPC
from .common import AutocompleteFieldRenderer
from webhelpers.html import literal
from edbob.pyramid.forms import pretty_datetime


__all__ = ['ProductFieldRenderer', 'GPCFieldRenderer',
           'BrandFieldRenderer', 'VendorFieldRenderer',
           'PriceFieldRenderer', 'PriceWithExpirationFieldRenderer']


class ProductFieldRenderer(AutocompleteFieldRenderer):
    """
    Renderer for :class:`rattail.db.model.Product` instance fields.
    """

    service_route = 'products.autocomplete'

    @property
    def field_display(self):
        product = self.raw_value
        if product:
            return product.full_description
        return ''


class GPCFieldRenderer(TextFieldRenderer):
    """
    Renderer for :class:`rattail.gpc.GPC` fields.
    """

    @property
    def length(self):
        # Hm, should maybe consider hard-coding this...?
        return len(str(GPC(0)))


class BrandFieldRenderer(AutocompleteFieldRenderer):
    """
    Renderer for :class:`rattail.db.model.Brand` instance fields.
    """

    service_route = 'brands.autocomplete'


class VendorFieldRenderer(AutocompleteFieldRenderer):
    """
    Renderer for :class:`rattail.db.model.Vendor` instance fields.
    """

    service_route = 'vendors.autocomplete'


class PriceFieldRenderer(TextFieldRenderer):
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
        result = super(PriceWithExpirationFieldRenderer, self).render_readonly(**kwargs)
        if result:
            price = self.field.raw_value
            if price.ends:
                result += '&nbsp; (%s)' % pretty_datetime(price.ends, from_='utc')
        return result
