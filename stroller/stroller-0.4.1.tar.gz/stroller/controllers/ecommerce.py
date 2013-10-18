# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import tmpl_context
from tw.api import WidgetsList
from tw.forms import TableForm, SingleSelectField, FormField, TextField
from tw.dynforms import OtherSingleSelectField, HidingContainerMixin, HidingSingleSelectField
from formencode import validators

from tg import expose, flash, require, url, request, redirect, session, TGController, config
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tgext.admin.tgadminconfig import TGAdminConfig
from tgext.admin.controller import AdminController
from repoze.what import predicates
from webob.exc import HTTPNotFound

from stroller.lib import stroller_url, style_css, send_email, confirm_css
from stroller.lib.cart import results, get_cart, drop_cart
from stroller.model.commerce import *
from stroller.model.core import DBSession, User, Group
from stroller.controllers.payment import PaymentController
from stroller.controllers.manage import ManageController
from stroller.controllers.widgets import QuantityOtherSingleSelectField

from tw.jquery import jquery_js

__all__ = ['StrollerController']

class NumberForm(TableForm):
    class fields(WidgetsList):
        quantity = QuantityOtherSingleSelectField(field='Quantity', label_text='Quantity')
create_number_form = NumberForm("create_number_form", submit_text = None)

class StrollerController(TGController):
    payment = PaymentController()
    admin = AdminController([Category, Product, ProductInfo], DBSession, config_type=TGAdminConfig)
    manage = ManageController()

    @expose('stroller.templates.index')
    def index(self):
        category = DBSession.query(Category).filter_by(name='Shop').first()
        front_categories = DBSession.query(Category).filter_by(featured=True).all()
        featured = DBSession.query(Product).filter_by(featured=True).all()
        favourites = DBSession.query(Product).order_by(Product.bought.desc())[:6]

        style_css.inject()
        return results(front_categories=front_categories,
                        featured=featured, favourites=favourites,
                        category=category)

    @expose('stroller.templates.featured')
    def featured(self):
        featured = DBSession.query(Product).filter_by(featured=True).all()            
        style_css.inject()
        return results( featured=featured)
        
    @expose('stroller.templates.category')
    def category(self, uid=None):
        category = DBSession.query(Category).filter_by(uid=uid).first()
        if not category:
            raise HTTPNotFound()

        if category.name == 'Shop':
            return redirect(stroller_url('/'))

        if not category.is_visible(request.identity and request.identity['user']):
            flash('You do not have access to this category')
            return redirect(stroller_url('/'))
            
        style_css.inject()
        return results(category=category)

    @expose(content_type='image/jpeg')
    def category_icon(self, uid=None):
        category = DBSession.query(Category).filter_by(uid=uid).first()
        if not category:
            raise HTTPNotFound()

        return category.icon

    @require(predicates.not_anonymous())
    @expose('stroller.templates.recap')
    def recap(self, uid=None, force_user=None):
        style_css.inject()

        user = request.identity['user']
        if force_user and bool(predicates.in_group('stroller')):
            user = DBSession.query(User).filter_by(user_id=force_user).first()

        orders = Order.find_by_data('user_id', user.user_id).filter(Order.confirmed==True).order_by(Order.uid.desc()).all()
        if not uid and orders:
            uid = orders[0].uid
        return dict(user=user, orders=orders, selected_order=uid)

    @expose('stroller.templates.product')
    def product(self, uid=None):
        product = DBSession.query(Product).filter_by(uid=uid).first()
        if not product:
            raise HTTPNotFound()

        if not product.category.is_visible(request.identity and request.identity['user']):
            flash('You do not have access to this product')
            return redirect(stroller_url('/'))
            
        jquery_js.inject()
        style_css.inject()
        return results(product=product, form=create_number_form)
        
    @expose('stroller.templates.search')
    def search(self, what=''):
        if not what or len(what) < 3:
            flash('Search too short', 'warning')
            return redirect(stroller_url('/'))

        category = DBSession.query(Category).filter_by(name='Shop').first()
        products = DBSession.query(Product).join(ProductInfo).filter(ProductInfo.name.like('%'+what+'%'))
            
        jquery_js.inject()
        style_css.inject()
        return results(what=what, products=products, category=category)
       
        
    @expose(content_type='image/jpeg')
    def product_thumb(self, uid=None, photo='main'):
        if photo == 'main':
            product = DBSession.query(Product).filter_by(uid=uid).first()
        else:
            product = DBSession.query(ProductPhoto).filter_by(uid=photo).first()

        if not product:
            raise HTTPNotFound()
        
        return product.thumb
        
    @expose(content_type='image/jpeg')
    def product_image(self, uid=None, photo='main'):
        if photo == 'main':
            product = DBSession.query(Product).filter_by(uid=uid).first()
        else:
            product = DBSession.query(ProductPhoto).filter_by(uid=photo).first()

        if not product:
            raise HTTPNotFound()

        return product.photo

    @expose('stroller.templates.cart')
    def cart(self):
        cart = get_cart()

        if cart.confirmed:
            flash(_('Order has been already confirmed and cannot be changed anymore'))
            drop_cart()
            return redirect(stroller_url('/'))

        if not cart.total_quantity:
            flash(_('Your cart is empty'))
            return redirect(stroller_url('/'))

        confirm_css.inject()
        return dict(cart=cart)

    @expose('json')
    def add_to_cart(self, product=None, qnt=1):
        try:
            qnt = int(qnt)
        except:
            qnt = 0

        cart = get_cart()
        if qnt > 0:
            product = Product.get(product)
            if product and cart:
                if product.in_stock(1):
                    cart.add_item(product, qnt)
                else:
                    flash(_('Product is currently not available'))
            
        return results(price=cart.total_price, quantity=cart.total_quantity)

    @expose('json')
    def del_from_cart(self, product=None, qnt=1):
        try:
            qnt = int(qnt)
        except:
            qnt = 0

        cart = get_cart()
        if qnt > 0:
            product = Product.get(product)
            if product and cart:
                cart.del_item(product, qnt)

        return results(price=cart.total_price, quantity=cart.total_quantity)

    @expose()
    def conclude(self, order=None):
        order = Order.get(order)
        if not order:
            flash(_('Order not found'))
            return redirect(stroller_url('/'))

        if not order.confirmed:
            flash(_('Order has never been confirmed'))
            return redirect(stroller_url('/'))

        if order.dispatched:
            flash(_('Order has already been dispatched'))
            return redirect(stroller_url('/'))

        stroller_order_mail = config.get('stroller_order_notify_mail', None)
        stroller_email_sender = config.get('stroller_email_sender', stroller_order_mail)
        customer = order.get_data_string('ship_name') or '<anonymous>'
        order_email =  order.get_data_string('email')
        customer_email = order_email or '<unknown email>'

        if stroller_order_mail:
            #Send email to manager to notify that user has bought an order
            send_email(stroller_email_sender, stroller_order_mail, '{0} placed an order'.format(customer),
                '''{0} placed order {1}'''.format(customer_email, stroller_url('/manage/show_order', qualified=True, uid=order.uid)))

        #If we have users enabled send an email to user to notify about his order
        if stroller_order_mail and order_email:
            if order.payed:
                end_message = 'Order registered as successfully payed.'
            else:
                end_message = 'Please proceed with the payment as described on the web site as soon as possible.'

            if order.get_data('user_id'):
                end_message += '\n\nCheck your order at {0}'.format(stroller_url('/recap', qualified=True, uid=order.uid))

            send_email(stroller_email_sender, customer_email, 'Order successfully placed', '''
Your order of {0} items, for a total of {1} {2} has been successfully registered.

{3}
'''.format(order.total_quantity, order.total_price, config.get('currency', 'EUR'), end_message))

        if not order.payed and (not stroller_order_mail or not order_email):
            flash(_('Order successfully registered, Please provide your order id either by telephone or fax to proceed with payment. Order ID: %s') % order.uid)
        else:
            flash(_('Order successfully registered'))

        return redirect(stroller_url('/'))
