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
Report Views
"""

from .core import View
from mako.template import Template
from pyramid.response import Response

from ..db import Session
from rattail.db.model import Vendor, Department, Product, ProductCost

import re
import rattail
from edbob.time import local_time
from rattail.files import resource_path


plu_upc_pattern = re.compile(r'^000000000(\d{5})$')
weighted_upc_pattern = re.compile(r'^002(\d{5})00000\d$')

def get_upc(product):
    upc = '%014u' % product.upc
    m = plu_upc_pattern.match(upc)
    if m:
        return str(int(m.group(1)))
    m = weighted_upc_pattern.match(upc)
    if m:
        return str(int(m.group(1)))
    return upc


class OrderingWorksheet(View):
    """
    This is the "Ordering Worksheet" report.
    """

    report_template_path = 'tailbone:reports/ordering_worksheet.mako'

    upc_getter = staticmethod(get_upc)

    def __call__(self):
        if self.request.params.get('vendor'):
            vendor = Session.query(Vendor).get(self.request.params['vendor'])
            if vendor:
                departments = []
                uuids = self.request.params.get('departments')
                if uuids:
                    for uuid in uuids.split(','):
                        dept = Session.query(Department).get(uuid)
                        if dept:
                            departments.append(dept)
                preferred_only = self.request.params.get('preferred_only') == '1'
                body = self.write_report(vendor, departments, preferred_only)
                response = Response(content_type='text/html')
                response.headers['Content-Length'] = len(body)
                response.headers['Content-Disposition'] = 'attachment; filename=ordering.html'
                response.text = body
                return response
        return {}

    def write_report(self, vendor, departments, preferred_only):
        """
        Rendering engine for the ordering worksheet report.
        """

        q = Session.query(ProductCost)
        q = q.join(Product)
        q = q.filter(ProductCost.vendor == vendor)
        q = q.filter(Product.department_uuid.in_([x.uuid for x in departments]))
        if preferred_only:
            q = q.filter(ProductCost.preference == 1)

        costs = {}
        for cost in q:
            dept = cost.product.department
            subdept = cost.product.subdepartment
            costs.setdefault(dept, {})
            costs[dept].setdefault(subdept, [])
            costs[dept][subdept].append(cost)

        def cost_sort_key(cost):
            product = cost.product
            brand = product.brand.name if product.brand else ''
            key = '{0} {1}'.format(brand, product.description)
            return key

        now = local_time()
        data = dict(
            vendor=vendor,
            costs=costs,
            cost_sort_key=cost_sort_key,
            date=now.strftime('%a %d %b %Y'),
            time=now.strftime('%I:%M %p'),
            get_upc=self.upc_getter,
            rattail=rattail,
            )

        template_path = resource_path(self.report_template_path)
        template = Template(filename=template_path)
        return template.render(**data)


class InventoryWorksheet(View):
    """
    This is the "Inventory Worksheet" report.
    """

    report_template_path = 'tailbone:reports/inventory_worksheet.mako'

    upc_getter = staticmethod(get_upc)

    def __call__(self):
        """
        This is the "Inventory Worksheet" report.
        """

        departments = Session.query(Department)

        if self.request.params.get('department'):
            department = departments.get(self.request.params['department'])
            if department:
                body = self.write_report(department)
                response = Response(content_type='text/html')
                response.headers['Content-Length'] = len(body)
                response.headers['Content-Disposition'] = 'attachment; filename=inventory.html'
                response.text = body
                return response

        departments = departments.order_by(rattail.Department.name)
        departments = departments.all()
        return{'departments': departments}

    def write_report(self, department):
        """
        Generates the Inventory Worksheet report.
        """

        def get_products(subdepartment):
            q = Session.query(rattail.Product)
            q = q.outerjoin(rattail.Brand)
            q = q.filter(rattail.Product.subdepartment == subdepartment)
            if self.request.params.get('weighted-only'):
                q = q.filter(rattail.Product.unit_of_measure == rattail.UNIT_OF_MEASURE_POUND)
            q = q.order_by(rattail.Brand.name, rattail.Product.description)
            return q.all()

        now = local_time()
        data = dict(
            date=now.strftime('%a %d %b %Y'),
            time=now.strftime('%I:%M %p'),
            department=department,
            get_products=get_products,
            get_upc=self.upc_getter,
            )

        template_path = resource_path(self.report_template_path)
        template = Template(filename=template_path)
        return template.render(**data)


def add_routes(config):
    config.add_route('reports.ordering',        '/reports/ordering')
    config.add_route('reports.inventory',       '/reports/inventory')


def includeme(config):
    add_routes(config)

    config.add_view(OrderingWorksheet, route_name='reports.ordering',
                    renderer='/reports/ordering.mako')

    config.add_view(InventoryWorksheet, route_name='reports.inventory',
                    renderer='/reports/inventory.mako')
