# -*- coding: utf-8 -*-

import conf
from django.forms import model_to_dict
from .signals import payment_process
from django.db import models


class Payment(models.Model):
    PAYMENT_CARD = 1
    PATMENT_UKASH = 13
    PATMENT_WEBMONEY = 15
    PATMENT_YANDEX_MONEY = 16
    PATMENT_QIWI = 21
    PATMENT_MAILRU = 150
    PATMENT_PAYCASH = 300
    PATMENT_MONEBOOKERS = 410
    PAYMENT_MODES_CHOICES = (
        (PAYMENT_CARD, 'Банковские карты'),
        (PATMENT_UKASH, 'Ukash'),
        (PATMENT_WEBMONEY, 'Webmoney'),
        (PATMENT_YANDEX_MONEY, 'Яндекс-Деньги'),
        (PATMENT_QIWI, 'Qiwi'),
        (PATMENT_MAILRU, 'money@mail.ru'),
        (PATMENT_PAYCASH, 'Счет Paymecash'),
        (PATMENT_MONEBOOKERS, 'Счет Monebookers'),
    )

    CURRENCY_RUB = 'RUB'
    CURRENCY_USD = 'USD'
    CURRENCY_CHOICES = (
        (CURRENCY_RUB, 'Рубли'),
        (CURRENCY_USD, 'Доллары'),
    )

    RESULT_OK = 'OK'
    RESULT_ERROR = 'ERROR'
    RESULT_CHOICES = (
        (RESULT_OK, 'Подьвержден'),
        (RESULT_ERROR, 'Ошибка'),
    )

    order_id = models.CharField('Номер заказа', max_length=16, unique=True)
    wallet_id = models.PositiveIntegerField('Номер кошелька', default=conf.PAYMECASH_WALLET_ID)
    product_price = models.DecimalField('Сумма', max_digits=9, decimal_places=2)
    product_currency = models.CharField('Валюта', max_length=3,
                                        default=conf.PAYMECASH_DEFAULT_CURRENCY, choices=CURRENCY_CHOICES)
    payment_type_group_id = models.PositiveSmallIntegerField('Способ платежа', blank=True, null=True,
                                                             choices=PAYMENT_MODES_CHOICES, default=PAYMENT_CARD)
    cs1 = models.CharField('CS1', max_length=255, blank=True, null=True)
    cs2 = models.CharField('CS2', max_length=255, blank=True, null=True)
    cs3 = models.CharField('CS3', max_length=255, blank=True, null=True)

    result = models.CharField('Статус', max_length=16, choices=RESULT_CHOICES, blank=True, null=True)
    transaction_id = models.PositiveSmallIntegerField('Номер транзакции', blank=True, null=True)

    updated = models.DateTimeField('Обновлен', auto_now=True)
    created = models.DateTimeField('Создан', auto_now_add=True)

    def __unicode__(self):
        return '%s <%s>' % (
            self.order_id,
            self.get_status_display()
        )

    def save(self, *args, **kwargs):
        if self.pk is None:
            data = model_to_dict(self)
            payment_process.send(sender=self, data=data)
        super(Payment, self).save(*args, **kwargs)

    class Meta:
        ordering = ('created',)
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'