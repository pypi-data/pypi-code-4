# -*- coding: utf-8 -*-

from django.views.generic import TemplateView
from paymecash.forms import PayForm
from cart.models import Goods
from cart.models import Order


class PayPageView(TemplateView):
    template_name = 'pay_page.html'

    def get_context_data(self, **kwargs):
        order = self.make_order()

        ctx = super(PayPageView, self).get_context_data(**kwargs)
        ctx['form'] = PayForm(initial={
            'order_id': order.order_id,
            'product_price': order.amount,
            'cs1': u'Описание заказа',
        })
        return ctx

    def make_order(self):
        item1, created = Goods.objects.get_or_create(name='Goods #1', price=100.)
        item2, created = Goods.objects.get_or_create(name='Goods #2', price=200.)

        order = Order(amount=item1.price + item2.price)
        order.save()
        order.goods.add(item1)
        order.goods.add(item2)
        order.save()

        return order