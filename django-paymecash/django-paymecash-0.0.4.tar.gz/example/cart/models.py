# -*- coding: utf-8 -*-

from django.db import models
from paymecash.common import get_order_id


class Goods(models.Model):
    name = models.CharField(max_length=8)
    price = models.DecimalField(max_digits=9, decimal_places=2)


class Order(models.Model):
    order_id = models.CharField(max_length=16, default=get_order_id)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    goods = models.ManyToManyField(Goods)