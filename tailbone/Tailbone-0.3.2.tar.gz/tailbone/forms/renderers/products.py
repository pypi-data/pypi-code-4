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


__all__ = ['GPCFieldRenderer', 'ProductFieldRenderer']


class GPCFieldRenderer(TextFieldRenderer):
    """
    Renderer for :class:`rattail.gpc.GPC` fields.
    """

    @property
    def length(self):
        # Hm, should maybe consider hard-coding this...?
        return len(str(GPC(0)))


class ProductFieldRenderer(TextFieldRenderer):
    """
    Renderer for fields which represent :class:`rattail.db.Product` instances.
    """

    def render_readonly(self, **kwargs):
        product = self.raw_value
        if product is None:
            return ''
        return product.full_description
