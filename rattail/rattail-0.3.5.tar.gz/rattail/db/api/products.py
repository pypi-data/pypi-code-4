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
``rattail.db.api.products`` -- Products API
"""

from sqlalchemy.orm.exc import NoResultFound

import rattail
from rattail.db.model import Product, ProductCode


__all__ = ['get_product_by_upc', 'get_product_by_code']


def get_product_by_upc(session, upc):
    """
    Returns the :class:`rattail.Product` associated with ``upc`` (if found), or
    ``None``.
    """

    q = session.query(rattail.Product)
    q = q.filter(rattail.Product.upc == upc)
    try:
        return q.one()
    except NoResultFound:
        return None


def get_product_by_code(session, code):
    """
    Locate a ``Product`` instance using a code value.

    :param session: An open SQLAlchemy session.

    :param code: Product code for which to search.
    :type code: string

    :returns: A :class:`rattail.db.model.Product` instance, or ``None``.

    .. note::
       This function will return the *first* product found, and does not warn
       if multiple products would have matched the search.
    """

    q = session.query(Product)\
        .outerjoin(ProductCode)\
        .filter(ProductCode.code == code)
    return q.first()
