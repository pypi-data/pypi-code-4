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
``rattail.db.cache`` -- Cache Helpers
"""

from sqlalchemy.orm import joinedload

import edbob
from edbob.util import requires_impl

import rattail
from rattail.db.model import (
    Department, Subdepartment, Family, Brand, Vendor, Product, CustomerGroup, Customer)


class DataCacher(edbob.Object):

    def __init__(self, session=None, **kwargs):
        super(DataCacher, self).__init__(session=session, **kwargs)

    @property
    @requires_impl(is_property=True)
    def class_(self):
        pass
    
    @property
    def name(self):
        return self.class_.__name__

    def query(self):
        return self.session.query(self.class_)

    def get_cache(self, progress):
        self.instances = {}

        query = self.query()
        count = query.count()
        if not count:
            return self.instances
        
        prog = None
        if progress:
            prog = progress("Caching {0} records".format(self.name), count)

        cancel = False
        for i, instance in enumerate(query, 1):
            self.cache_instance(instance)
            if prog and not prog.update(i):
                cancel = True
                break

        if prog:
            prog.destroy()

        if cancel:
            session.close()
            return None
        return self.instances


class DepartmentCacher(DataCacher):

    class_ = Department

    def cache_instance(self, dept):
        self.instances[dept.number] = dept


class SubdepartmentCacher(DataCacher):

    class_ = Subdepartment

    def cache_instance(self, subdept):
        self.instances[subdept.number] = subdept


class FamilyCacher(DataCacher):

    class_ = Family

    def cache_instance(self, family):
        self.instances[family.code] = family


class BrandCacher(DataCacher):

    class_ = Brand

    def cache_instance(self, brand):
        self.instances[brand.name] = brand


class VendorCacher(DataCacher):

    class_ = Vendor

    def cache_instance(self, vend):
        self.instances[vend.id] = vend


class ProductCacher(DataCacher):

    class_ = Product
    with_costs = False

    def query(self):
        q = self.session.query(Product)
        if self.with_costs:
            q = q.options(joinedload(Product.costs))
            q = q.options(joinedload(Product.cost))
        return q

    def cache_instance(self, prod):
        self.instances[prod.upc] = prod


def get_product_cache(session, with_costs=False, progress=None):
    """
    Cache the full product set by UPC.

    Returns a dictionary of all existing products, keyed by
    :attr:`rattail.Product.upc`.
    """

    cacher = ProductCacher(session=session, with_costs=with_costs)
    return cacher.get_cache(progress)


class CustomerGroupCacher(DataCacher):

    class_ = CustomerGroup

    def cache_instance(self, group):
        self.instances[group.id] = group


class CustomerCacher(DataCacher):

    class_ = Customer

    def cache_instance(self, customer):
        self.instances[customer.id] = customer
