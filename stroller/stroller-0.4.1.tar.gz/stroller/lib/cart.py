# -*- coding: utf-8 -*-

from tg import request, session
from stroller.model.commerce import Order
from stroller.model.core import DBSession

__all__ = ['get_cart', 'drop_cart', 'results']

def get_cart():
    cart = session.get('cartid', None)
    cart = Order.get(cart)

    if not cart or cart.payed:
        cart = Order()
        DBSession.add(cart)
        DBSession.flush()
        session['cartid'] = cart.uid
        session.save()

    return cart

def drop_cart():
    cart = session.get('cartid', None)
    cart = Order.get(cart)

    if cart:
        del session['cartid']
        session.save()

def results(cart=None, **kw):
    if not cart:
        cart = get_cart()
    kw['cart'] = cart
    return kw

