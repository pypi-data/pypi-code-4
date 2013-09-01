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
Product Views
"""

from sqlalchemy import and_
from sqlalchemy.orm import joinedload

from webhelpers.html.tags import link_to

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response

import edbob
from edbob.pyramid.progress import SessionProgress
from . import SearchableAlchemyGridView

import rattail.labels
from rattail import sil
from rattail import batches
from rattail.threads import Thread
from rattail.exceptions import LabelPrintingError
from rattail.db.model import (
    Product, ProductPrice, ProductCost, ProductCode,
    Brand, Vendor, Department, Subdepartment, LabelProfile)
from rattail.gpc import GPC

from .. import Session
from ..forms import AutocompleteFieldRenderer, GPCFieldRenderer, PriceFieldRenderer
from . import CrudView


class ProductsGrid(SearchableAlchemyGridView):

    mapped_class = Product
    config_prefix = 'products'
    sort = 'description'

    def join_map(self):

        def join_vendor(q):
            q = q.outerjoin(
                ProductCost,
                and_(
                    ProductCost.product_uuid == Product.uuid,
                    ProductCost.preference == 1,
                    ))
            q = q.outerjoin(Vendor)
            return q

        return {
            'brand':
                lambda q: q.outerjoin(Brand),
            'department':
                lambda q: q.outerjoin(Department,
                                      Department.uuid == Product.department_uuid),
            'subdepartment':
                lambda q: q.outerjoin(Subdepartment,
                                      Subdepartment.uuid == Product.subdepartment_uuid),
            'regular_price':
                lambda q: q.outerjoin(ProductPrice,
                                      ProductPrice.uuid == Product.regular_price_uuid),
            'current_price':
                lambda q: q.outerjoin(ProductPrice,
                                      ProductPrice.uuid == Product.current_price_uuid),
            'vendor':
                join_vendor,
            'code':
                lambda q: q.outerjoin(ProductCode),
            }

    def filter_map(self):

        def filter_upc():

            def filter_is(q, v):
                if not v:
                    return q
                try:
                    return q.filter(Product.upc.in_((
                                GPC(v), GPC(v, calc_check_digit='upc'))))
                except ValueError:
                    return q

            def filter_not(q, v):
                if not v:
                    return q
                try:
                    return q.filter(~Product.upc.in_((
                                GPC(v), GPC(v, calc_check_digit='upc'))))
                except ValueError:
                    return q

            return {'is': filter_is, 'nt': filter_not}

        return self.make_filter_map(
            ilike=['description', 'size'],
            upc=filter_upc(),
            brand=self.filter_ilike(Brand.name),
            department=self.filter_ilike(Department.name),
            subdepartment=self.filter_ilike(Subdepartment.name),
            vendor=self.filter_ilike(Vendor.name),
            code=self.filter_ilike(ProductCode.code))

    def filter_config(self):
        return self.make_filter_config(
            include_filter_upc=True,
            filter_type_upc='eq',
            filter_label_upc="UPC",
            include_filter_brand=True,
            filter_type_brand='lk',
            include_filter_description=True,
            filter_type_description='lk',
            include_filter_department=True,
            filter_type_department='lk',
            include_filter_vendor=True,
            filter_type_vendor='lk')

    def sort_map(self):
        return self.make_sort_map(
            'upc', 'description', 'size',
            brand=self.sorter(Brand.name),
            department=self.sorter(Department.name),
            subdepartment=self.sorter(Subdepartment.name),
            regular_price=self.sorter(ProductPrice.price),
            current_price=self.sorter(ProductPrice.price),
            vendor=self.sorter(Vendor.name))

    def query(self):
        q = self.make_query()
        q = q.options(joinedload(Product.brand))
        q = q.options(joinedload(Product.department))
        q = q.options(joinedload(Product.subdepartment))
        q = q.options(joinedload(Product.regular_price))
        q = q.options(joinedload(Product.current_price))
        q = q.options(joinedload(Product.vendor))
        return q

    def grid(self):
        g = self.make_grid()
        g.upc.set(renderer=GPCFieldRenderer)
        g.regular_price.set(renderer=PriceFieldRenderer)
        g.current_price.set(renderer=PriceFieldRenderer)
        g.configure(
            include=[
                g.upc.label("UPC"),
                g.brand,
                g.description,
                g.size,
                g.subdepartment,
                g.vendor,
                g.regular_price.label("Reg. Price"),
                g.current_price.label("Cur. Price"),
                ],
            readonly=True)

        if self.request.has_perm('products.read'):
            g.viewable = True
            g.view_route_name = 'product.read'
        if self.request.has_perm('products.update'):
            g.editable = True
            g.edit_route_name = 'product.update'
        if self.request.has_perm('products.delete'):
            g.deletable = True
            g.delete_route_name = 'product.delete'

        q = Session.query(LabelProfile)
        if q.count():
            def labels(row):
                return link_to("Print", '#', class_='print-label')
            g.add_column('labels', "Labels", labels)

        return g

    def render_kwargs(self):
        q = Session.query(LabelProfile)
        q = q.filter(LabelProfile.visible == True)
        q = q.order_by(LabelProfile.ordinal)
        return {'label_profiles': q.all()}


class ProductCrud(CrudView):

    mapped_class = Product
    home_route = 'products'

    def get_model(self, key):
        model = super(ProductCrud, self).get_model(key)
        if model:
            return model
        model = Session.query(ProductPrice).get(key)
        if model:
            return model.product
        return None

    def fieldset(self, model):
        fs = self.make_fieldset(model)
        fs.upc.set(renderer=GPCFieldRenderer)
        fs.brand.set(renderer=AutocompleteFieldRenderer(
                self.request.route_url('brands.autocomplete')))
        fs.regular_price.set(renderer=PriceFieldRenderer)
        fs.current_price.set(renderer=PriceFieldRenderer)
        fs.configure(
            include=[
                fs.upc.label("UPC"),
                fs.brand,
                fs.description,
                fs.size,
                fs.department,
                fs.subdepartment,
                fs.regular_price,
                fs.current_price,
                ])
        if not self.readonly:
            del fs.regular_price
            del fs.current_price
        return fs


def print_labels(request):
    profile = request.params.get('profile')
    profile = Session.query(LabelProfile).get(profile) if profile else None
    if not profile:
        return {'error': "Label profile not found"}

    product = request.params.get('product')
    product = Session.query(Product).get(product) if product else None
    if not product:
        return {'error': "Product not found"}

    quantity = request.params.get('quantity')
    if not quantity.isdigit():
        return {'error': "Quantity must be numeric"}
    quantity = int(quantity)

    printer = profile.get_printer()
    if not printer:
        return {'error': "Couldn't get printer from label profile"}

    try:
        printer.print_labels([(product, quantity)])
    except Exception, error:
        return {'error': str(error)}
    return {}


class CreateProductsBatch(ProductsGrid):

    def make_batch(self, provider, progress):
        from rattail.db import Session
        session = Session()

        self._filter_config = self.filter_config()
        self._sort_config = self.sort_config()
        products = self.make_query(session)

        batch = provider.make_batch(session, products, progress)
        if not batch:
            session.rollback()
            session.close()
            return

        session.commit()
        session.refresh(batch)
        session.close()

        progress.session.load()
        progress.session['complete'] = True
        progress.session['success_url'] = self.request.route_url('batch.read', uuid=batch.uuid)
        progress.session['success_msg'] = "Batch \"%s\" has been created." % batch.description
        progress.session.save()

    def __call__(self):
        if self.request.POST:
            provider = self.request.POST.get('provider')
            if provider:
                provider = batches.get_provider(provider)
                if provider:

                    if self.request.POST.get('params') == 'True':
                        provider.set_params(Session(), **self.request.POST)

                    else:
                        try:
                            url = self.request.route_url('batch_params.%s' % provider.name)
                        except KeyError:
                            pass
                        else:
                            self.request.session['referer'] = self.request.current_route_url()
                            return HTTPFound(location=url)
                    
                    progress = SessionProgress(self.request.session, 'products.batch')
                    thread = Thread(target=self.make_batch, args=(provider, progress))
                    thread.start()
                    kwargs = {
                        'key': 'products.batch',
                        'cancel_url': self.request.route_url('products'),
                        'cancel_msg': "Batch creation was canceled.",
                        }
                    return render_to_response('/progress.mako', kwargs, request=self.request)

        enabled = edbob.config.get('rattail.pyramid', 'batches.providers')
        if enabled:
            enabled = enabled.split()

        providers = []
        for provider in batches.iter_providers():
            if not enabled or provider.name in enabled:
                providers.append((provider.name, provider.description))

        return {'providers': providers}


def add_routes(config):
    config.add_route('products', '/products')
    config.add_route('products.print_labels', '/products/labels')
    config.add_route('products.create_batch', '/products/batch')
    config.add_route('product.create', '/products/new')
    config.add_route('product.read', '/products/{uuid}')
    config.add_route('product.update', '/products/{uuid}/edit')
    config.add_route('product.delete', '/products/{uuid}/delete')
    

def includeme(config):
    add_routes(config)

    config.add_view(ProductsGrid, route_name='products',
                    renderer='/products/index.mako',
                    permission='products.list')
    config.add_view(print_labels, route_name='products.print_labels',
                    renderer='json', permission='products.print_labels')
    config.add_view(CreateProductsBatch, route_name='products.create_batch',
                    renderer='/products/batch.mako',
                    permission='batches.create')
    config.add_view(ProductCrud, attr='create', route_name='product.create',
                    renderer='/products/crud.mako',
                    permission='products.create')
    config.add_view(ProductCrud, attr='read', route_name='product.read',
                    renderer='/products/read.mako',
                    permission='products.read')
    config.add_view(ProductCrud, attr='update', route_name='product.update',
                    renderer='/products/crud.mako',
                    permission='products.update')
    config.add_view(ProductCrud, attr='delete', route_name='product.delete',
                    permission='products.delete')
