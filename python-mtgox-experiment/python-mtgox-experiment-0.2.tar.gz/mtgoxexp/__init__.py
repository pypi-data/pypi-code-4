# -*- coding: utf-8 -*-
"""\
2013-05-07 R.R. Nederhoed

This module implements only the calls needed to receive, buy, sell and send BTC.
It does not aspire to build an implementation of the complete API.

Webshop
* create a BTC address with IPN for payment notification
* on payment, we want to sell the BTC on the market
Bitcoin selling
* buy BTC 
* send it to the customer

In both cases we need the be able to request pricing info.

TODO: error handling with useful values
TODO: add jsonascii for non-ascii chars in the description of get_new_address
TODO: unit tests
"""
import time
import urllib
import urllib2
import json
from decimal import Decimal

import hmac
from hashlib import sha512
import base64

from decorators import cached_property

def satoshi2decimal(satoshis):
    """Convert an integer Bitcoin amount to decimal
    >>> v = 1  # 1 satoshi
    >>> satoshi2decimal(v)
    Decimal('1E-8')
    """
    return Decimal("%.8f"%(satoshis/100000000.))

def decimal2satoshi(value):
    """Convert a decimal value to satoshis
    >>> v = Decimal('0.00000001')  # 1 satoshi
    >>> decimal2satoshi(v)
    1L
    """
    return long(value*100000000)


class MtGoxAccess(object):
    """Authentication to the API """
    url_api = "https://data.mtgox.com/api/2/"
    
    def __init__(self, key, secret, client="Experimental Bitcoin Client v0.1"):
        self._key = key
        self._secret = secret
        self._client = client
    
    def _get_signature(self, path, data):
        hash_data = path + chr(0) + data
        h = hmac.new(base64.b64decode(self._secret), hash_data, sha512)
        return base64.b64encode(str(h.digest()))
    
    def call(self, path, data):
        """ """
        url = MtGoxAccess.url_api + path
        nonce = long(100*time.time())  # max 100 requests per second
        if data is None:
            data = {'nonce' : nonce}
        else:
            data.update({'nonce' : nonce})
        # Encode
        data = urllib.urlencode(data)
        request = urllib2.Request(url, data)
        # Sign
        request.add_header("User-Agent", self._client)
        request.add_header('Rest-Key', self._key)
        request.add_header('Rest-Sign', self._get_signature(path, data))
        # Retrieve info
        result = json.load(urllib2.urlopen(request))
        if result['result'] == 'success':
            return result
        else:
            raise ValueError(result['error'])


class Account(object):
    """New address with IPN URL callback """
    def __init__(self, mtgox_access):
        """Trade on MtGox """
        self.mtgox = mtgox_access
    
    @cached_property(ttl=3)
    def info(self):
        """Get info on the current account 
        
        This data will be cached for 3 seconds
        """
        path = "money/info"
        data = {}
        # TODO: Error handling???
        return self.mtgox.call(path, data)['data']
    
    def balance(self, currency='BTC'):
        """Amount in account 
        
        This data will be cached for 3 seconds
        """
        data = self.info[u'Wallets'][currency][u'Balance']
        return Decimal(data['value'])
    
    def available(self, currency='BTC'):
        """Amount available for withdrawal
        
        This data will be cached for 3 seconds
        """
        data = self.info[u'Wallets'][currency]
        balance = Decimal(data[u'Balance'][u'value'])
        limit = Decimal(data[u'Max_Withdraw'][u'value'])
        return min(balance, limit)
    
    def max_withdraw(self, currency='BTC'):
        """Actual withdraw limit on the given currency
        
        This data will be cached for 3 seconds
        """
        data = self.info[u'Wallets'][currency]
        limit = Decimal(data[u'Max_Withdraw'][u'value'])
        return limit

    def send_btc(self, address, amount, fee=Decimal('0.0005')):
        """Send the given amount to the given address 
        address
        amount as Decimal
        fee as Decimal
        (no_instant, green)
        Note: You are not able to perform this method if you have enabled 
        Two-Factor authentication for withdrawals.
        
        We default to no_instant, not green with a fee of 0.0005.
        
        Returns the BTC transaction ID on success
        """
        path = "money/bitcoin/send_simple"
        data = {
            'address': address,
            # Convert Decimal amount to int
            'amount_int': decimal2satoshi(amount),
            'fee_int': decimal2satoshi(fee),
            'no_instant': True,
            'green': False,
        }
        return self.mtgox.call(path, data)[u'data'][u'trx']
    
    def get_new_address(self, description='', ipn_url=None):
        """Request a new btc_address 
        
        Description should be unique for a new address to be created.
        
        Returns the new address on success.
        """
        path = "money/bitcoin/address"
        data = {'description': description}
        if ipn_url:
            data['ipn'] = ipn_url
        result = self.mtgox.call(path, data)
        return result['data']['addr']


class Trade(object):
    """ """
    def __init__(self, mtgox_access):
        """Trade on MtGox """
        self.mtgox = mtgox_access
    
    def orders(self, market):
        """View open orders 
        parameters:
        
        """
        path = "%s/money/orders" % market
        data = {}
        result = self.mtgox.call(path, data)
        return result['data']

    def add(self, market, type_,amount, price=None):
        """Place order 
        To buy 0.5 BTC for max 60 euro per BTC, call:
        api.add('BTCEUR', 'bid', Decimal('0.5'), Decimal('60'))
        To sell 500 BTC for market price, call:
        api.add('BTCEUR', 'ask', Decimal('500'))
        """
        path = "%s/money/order/add" % market
        assert type_ in ('bid', 'ask')
        assert isinstance(amount, Decimal)
        # Convert amount Decimal to int
        data = {
            'type': type_,
            'amount_int': decimal2satoshi(amount),
        }
        # On price, convert to int
        if price is not None:
            assert isinstance(price, Decimal)
            data['price_int'] = long(price*100000)
        result = self.mtgox.call(path, data)
        return result['data']

    def cancel(self, market, order_id):
        """Cancel order """
        path = "%s/money/order/cancel" % market
        data = {
            'oid': order_id,
        }
        result = self.mtgox.call(path, data)
        return result['data']

if __name__ == "__main__":
    import doctest
    doctest.testmod()