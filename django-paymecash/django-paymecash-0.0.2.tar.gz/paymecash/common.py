# -*- coding: utf-8 -*-

import uuid
import conf
import hashlib


def get_sign(data):
    parts = [str(int(data['wallet_id']))]
    if data.get('product_price') is not None and data.get('product_currency') is not None:
        parts.append(str(data['product_price']))
        parts.append(data['product_currency'])
    if data.get('order_id'):
        parts.append(data['order_id'])
    parts.append(conf.PAYMECASH_SECRET_KEY)
    string = '-'.join(parts)
    sign = hashlib.md5(string).hexdigest()
    return sign


def get_order_id():
    return str(uuid.uuid4()).replace('-', '')[:16]