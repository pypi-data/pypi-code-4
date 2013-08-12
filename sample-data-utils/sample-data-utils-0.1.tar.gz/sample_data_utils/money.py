# -*- coding: utf-8 -*-
import decimal
from random import choice, uniform
import sys


def amount(min=1, max=sys.maxsize, decimal_places=2):
    """
        return a random floating number

    :param min: minimum value
    :param max: maximum value
    :param decimal_places: decimal places
    :return:
    """
    q = '.%s1' % '0' * (decimal_places - 1)
    return decimal.Decimal(uniform(min, max)).quantize(decimal.Decimal(q))


def currency():
    """
        returns a random ISO 4217 currency code

    """
    codes = ['AFN', 'ALL', 'DZD', 'USD', 'EUR', 'AOA', 'XCD', 'XCD', 'XCD', 'ARS', 'AMD', 'AWG', 'AUD', 'EUR', 'AZN',
             'BSD', 'BHD', 'BDT', 'BBD', 'BYR', 'EUR', 'BZD', 'XOF', 'BMD', 'BTN', 'BOB', 'BAM', 'BWP', 'NOK', 'BRL',
             'USD', 'BND', 'BGN', 'XOF', 'BIF', 'KHR', 'XAF', 'CAD', 'CVE', 'KYD', 'XAF', 'XAF', 'CLP', 'CNY', 'AUD',
             'AUD', 'COP', 'KMF', 'XAF', 'CDF', 'NZD', 'CRC', 'HRK', 'CUP', 'EUR', 'CZK', 'DKK', 'DJF', 'XCD', 'DOP',
             'ECS', 'EGP', 'SVC', 'XAF', 'ERN', 'EUR', 'ETB', 'EUR', 'FKP', 'DKK', 'FJD', 'EUR', 'EUR', 'EUR', 'EUR',
             'XAF', 'GMD', 'GEL', 'EUR', 'GHS', 'GIP', 'GBP', 'EUR', 'DKK', 'XCD', 'EUR', 'USD', 'QTQ', 'GGP', 'GNF',
             'GWP', 'GYD', 'HTG', 'AUD', 'HNL', 'HKD', 'HUF', 'ISK', 'INR', 'IDR', 'IRR', 'IQD', 'EUR', 'GBP', 'ILS',
             'EUR', 'XOF', 'JMD', 'JPY', 'GBP', 'JOD', 'KZT', 'KES', 'AUD', 'KPW', 'KRW', 'KWD', 'KGS', 'LAK', 'LVL',
             'LBP', 'LSL', 'LRD', 'LYD', 'CHF', 'LTL', 'EUR', 'MOP', 'MKD', 'MGF', 'MWK', 'MYR', 'MVR', 'XOF', 'EUR',
             'USD', 'EUR', 'MRO', 'MUR', 'EUR', 'MXN', 'USD', 'MDL', 'EUR', 'MNT', 'EUR', 'XCD', 'MAD', 'MZN', 'MMK',
             'NAD', 'AUD', 'NPR', 'EUR', 'ANG', 'XPF', 'NZD', 'NIO', 'XOF', 'NGN', 'NZD', 'AUD', 'USD', 'NOK', 'OMR',
             'PKR', 'USD', 'PAB', 'PGK', 'PYG', 'PEN', 'PHP', 'NZD', 'PLN', 'XPF', 'EUR', 'USD', 'QAR', 'EUR', 'RON',
             'RUB', 'RWF', 'SHP', 'XCD', 'XCD', 'EUR', 'XCD', 'WST', 'EUR', 'STD', 'SAR', 'XOF', 'RSD', 'SCR', 'SLL',
             'SGD', 'EUR', 'EUR', 'SBD', 'SOS', 'ZAR', 'GBP', 'SSP', 'EUR', 'LKR', 'SDG', 'SRD', 'NOK', 'SZL', 'SEK',
             'CHF', 'SYP', 'TWD', 'TJS', 'TZS', 'THB', 'XOF', 'NZD', 'TOP', 'TTD', 'TND', 'TRY', 'TMT', 'USD', 'AUD',
             'GBP', 'UGX', 'UAH', 'AED', 'UYU', 'USD', 'USD', 'UZS', 'VUV', 'EUR', 'VEF', 'VND', 'USD', 'USD', 'XPF',
             'MAD', 'YER', 'ZMW', 'ZWD']
    return choice(codes)
