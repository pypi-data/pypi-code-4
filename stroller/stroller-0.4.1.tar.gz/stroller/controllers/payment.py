from tg import expose, flash, require, url, request, redirect, session, TGController, config
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates
from webob.exc import HTTPNotFound

from stroller.lib import stroller_url, confirm_css
from stroller.lib.cart import results, get_cart, drop_cart
from stroller.lib.paypal import PayPal, ResponseError

from stroller.model.commerce import *

from tw.jquery import jquery_js

__all__ = ['PaymentController']

class PaymentController(TGController):
    @expose()
    def index(self):
        cart = get_cart()

        Order.clear_unconfirmed(cart)

        if not cart.total_quantity:
            flash(_('Your cart is empty'))
            return redirect(stroller_url('/'))

        if config.get('avoid_manage_payment', False):
            return redirect(stroller_url('/payment/confirm_static', qualified=True))

        p = PayPal()
        try:

            r = p.call('SetExpressCheckout', amt=cart.total_price, landingpage='Billing',
                                             currencycode=config.get('currency', 'EUR'),
                                             returnurl=stroller_url('/payment/confirm', qualified=True), 
                                             cancelurl=stroller_url('/payment/cancel', qualified=True))
        except ResponseError, e:
            flash(_('There has been an error in processing your payment request: %s') % e)
            return redirect(stroller_url('/'))

        return redirect(p.express_checkout_url(r.tokens['TOKEN']))
        
    @expose()
    def cancel(self, **kw):
        cart = get_cart()
        drop_cart()
        flash(_('Your transaction has been revoked'))
        return redirect(stroller_url('/'))        
    
    @expose()
    def cancel_static(self, **kw):
        flash(_('Your Cart was reset'))
        cart = get_cart()
        drop_cart()
        return redirect(stroller_url('/'))
    
    @expose('stroller.templates.payment.confirm')
    def confirm_static(self, **kw):
        cart = get_cart()

        if not cart.total_quantity:
            flash(_('Your cart is empty'))
            return redirect(stroller_url('/'))

        if request.identity and request.identity['user']:
            cart.set_data('email', request.identity['user'].email_address)
            cart.set_data('ship_name', request.identity['user'].display_name)
            cart.set_data('user_id', request.identity['user'].user_id)

        confirm_css.inject()
        return results(proceed_url=stroller_url('/payment/proceed_static'), static_confirm=True)
            
    @expose()
    def proceed_static(self, **kw):
        cart = get_cart()
        drop_cart()

        cart.confirm_order()
        cart.payed = False

        return redirect(stroller_url('/conclude', order=cart.uid))

    @expose('stroller.templates.payment.confirm')
    def confirm(self, **kw):
        cart = get_cart()

        if not cart.total_quantity:
            flash(_('Your cart is empty'))
            return redirect(stroller_url('/'))

        p = PayPal()
        try:
            r = p.call('GetExpressCheckoutDetails', token=kw['token'], currencycode=config.get('currency', 'EUR'))
        except ResponseError, e:
            flash('There has been an error in processing your payment request: %s' % e)
        
        if r.tokens['TOKEN'] != kw['token']:
            flash("Paypal didn't confirm the payment token, payment considered invalid")
            return redirect(stroller_url('/'))

        r.tokens['SHIPTOSTATE'] = r.tokens.get('SHIPTOSTATE', '')
        r.tokens['SHIPTOZIP'] = r.tokens.get('SHIPTOZIP', '')

        unicode_tokens = {}
        for key, value in r.tokens.iteritems():
            unicode_tokens[key] = value.decode('utf-8')

        cart.set_data('first_name', unicode_tokens['FIRSTNAME'])
        cart.set_data('last_name', unicode_tokens['LASTNAME'])
        if request.identity and request.identity['user']:
            cart.set_data('user_id', request.identity['user'].user_id)
            cart.set_data('email', request.identity['user'].email_address)
        else:
            cart.set_data('email', unicode_tokens['EMAIL'])
        cart.set_data('paypal_email', unicode_tokens['EMAIL'])
        cart.set_data('ship_name', unicode_tokens['SHIPTONAME'])
        cart.set_data('ship_address', unicode_tokens['SHIPTOSTREET'])
        cart.set_data('ship_zip', unicode_tokens['SHIPTOZIP'])
        cart.set_data('ship_city', unicode_tokens['SHIPTOCITY'])
        cart.set_data('ship_state', unicode_tokens['SHIPTOSTATE'])
        cart.set_data('ship_country', unicode_tokens['SHIPTOCOUNTRYNAME'])
        
        confirm_css.inject()
        return results(userdata=unicode_tokens, token=kw['token'], payerid=kw['PayerID'],
                       proceed_url=stroller_url('/payment/proceed'), static_confirm=False)
        
    @expose()
    def proceed(self, **kw):
        token = kw['token']
        payer = kw['payerid']
        amount = kw['total']

        cart = get_cart()
        cart.confirm_order()

        p = PayPal()
        try:
            r = p.call('DoExpressCheckoutPayment', paymentaction="Sale", token=token, payerid=payer,
                                                   currencycode=config.get('currency', 'EUR'), amt=amount)
        except ResponseError, e:
            flash('There has been an error processing your payment: %s' % e)
            return redirect(stroller_url('/'))

        drop_cart()
        cart.payed = True
        return redirect(stroller_url('/conclude', order=cart.uid))
        
