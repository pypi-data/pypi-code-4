# coding=utf-8

import requests
import logging
import time
logger = logging.getLogger(__name__)

try:  # python3 compatibility
    import urllib.parse as urlparse
except ImportError:
    import urlparse

try:  # i prefer ultrajson encoder
    import ujson as json
except ImportError:
    import json

from . import ZOOZ_SANDBOX
from .utils import backoff_retry
from .exceptions import ZoozException


ZOOZ_API_VERSION = '1.0.4'
ZOOZ_URLS = {
    'production': 'https://app.zooz.com/',
    'sandbox': 'https://sandbox.zooz.co/',
}


class ZoozRequestBase(object):
    """
        Base client for the Zooz API
    """

    def __init__(self, *args, **kwargs):
        self.requests = requests.Session()

    @property
    def get_url(self):
        global ZOOZ_SANDBOX
        global ZOOZ_URLS

        if ZOOZ_SANDBOX:
            return ZOOZ_URLS['sandbox']
        else:
            return ZOOZ_URLS['production']

    @backoff_retry(retries=5)
    def post(self, url, payload, headers):
        """
            Add authentication headers to the request
        """
        return self.requests.post(url, data=payload, headers=headers)

    def _parse_response_nvp(self, response):
        """
            parse_qs will build a dictionary of {key: [list]}, this will return
            a plain dict
        """
        response_dict = urlparse.parse_qs(response, keep_blank_values=True)

        return {k: v[0] for (k, v) in response_dict.items()}


class ZoozRequest(ZoozRequestBase):
    """
        Client for the ZooZ Server API

        Go to https://app.zooz.com/portal/PortalController?cmd=resources to
        see complete API documentation

        For authentication, some keys are needed:

            unique_id: as registered in the ZooZ developer portal
            app_key: as received upon registration

        By default, requests will be done to the 'production' ZooZ servers,
        so all transactions and payment will be real, to allow 'sandbox' mode
        just change the global variable ZOOZ_SANDBOX

            ZOOZ_SANDBOX = True
    """
    def __init__(self, unique_id, app_key):
        self.unique_id = unique_id
        self.app_key = app_key
        super(ZoozRequest, self).__init__()

    @property
    def get_url(self):
        """
            Returns the final URI needed to do requests to the secured servlet
        """
        return super(ZoozRequest, self).get_url + 'mobile/SecuredWebServlet'

    def add_authentication(self):
        headers = {
            'ZooZUniqueID': self.unique_id,
            'ZooZAppKey': self.app_key,
            'ZooZResponseType': 'NVP'
        }
        return headers

    def open_transaction(self, amount, currency_code, extra=None):
        """
            Open a transaction using a secured channel to ZooZ.

                amount: The amount to pay.
                currency_code: ISO code of the currency used to pay.

                Optional parametres can be used, use extra and a dict
                for a list of parameters name, see
                    ZooZ mobile web developer guide.

            :returns: Unique token used to identify the transaction.

                'statusCode': If equals to zero, request succeeded
                'errorMessage': Will contain the error message
                'token': Token generated

            :raises: ZoozException in case request fails
        """

        payload = {
            'cmd': 'openTrx',
            'amount': amount,
            'currencyCode': currency_code,
        }

        if extra:
            payload.update(extra)

        headers = self.add_authentication()
        logger.debug('[ZOOZ] open transaction: %s', payload)
        response = self._parse_response_nvp(
            self.post(self.get_url, payload, headers).text)
        if int(response['statusCode']) != 0:
            raise ZoozException(
                response['errorMessage'], response['statusCode'])
        return response


class ZoozRequestExtended(ZoozRequestBase):
    """
        Client for the ZooZ Extended Server API

        Go to https://app.zooz.com/portal/PortalController?cmd=resources to
        see complete API documentation

            developer_id: developer email used to log in ZooZ Developers portal
            app_key: Server API Key found in ZooZ portal -> My Account

        By default, requests will be done to the 'production' ZooZ servers,
        so all transactions and payment will be real, to allow 'sandbox' mode
        just change the global variable ZOOZ_SANDBOX

            ZOOZ_SANDBOX = True
    """

    def __init__(self, developer_id, api_key):
        self.developer_id = developer_id
        self.api_key = api_key
        super(ZoozRequestExtended, self).__init__()

    @property
    def get_url(self):
        """
            Returns the final URI needed to do requests to extended API
        """
        return super(
            ZoozRequestExtended, self).get_url + 'mobile/ExtendedServerAPI'

    def add_authentication(self):
        headers = {
            'ZooZDeveloperId': self.developer_id,
            'ZooZServerAPIKey': self.api_key,
        }
        return headers

    def get_transaction(self, transaction_id):
        """
            Get the info about a transaction using its ID

            :returns: a dict with two keys:
                'ResponseStatus': 0 if all is correct
                'ResponseObject': transaction info, see ZooZExtendedAPI doc.

            :raises: ZoozException in case request fails
        """
        assert transaction_id

        payload = {
            'cmd': 'getTransactionDetails',
            'ver': ZOOZ_API_VERSION,
            'transactionID': transaction_id,
        }
        headers = self.add_authentication()
        logger.debug('[ZOOZ] get transaction with payload: %s', payload)
        response = self.post(self.get_url, payload, headers).json()
        if int(response['ResponseStatus']) != 0:
            raise ZoozException(
                response['ResponseObject']['errorMessage'],
                response['ResponseStatus'])
        return response

    def get_transactions(self, user_email, from_date=None, to_date=None):
        """
            Get the list of transaction generated by an user.

            Allows filtering by date, date should be in the format: YYYY-mm-dd

            :returns: a dict with two keys:
                'ResponseStatus': 0 if all is correct.
                'ResponseObject': transaction info, see ZooZExtendedAPI doc.

            :raises: ZoozException in case request fails
        """
        assert user_email

        payload = {
            'cmd': 'getTransactionDetailsByPayerEmail',
            'ver': ZOOZ_API_VERSION,
            'email': user_email,
            'fromDate': from_date,
            'toDate': to_date,
        }
        headers = self.add_authentication()
        logger.debug('[ZOOZ] get transactions for user: %s', payload)
        response = self.post(self.get_url, payload, headers).json()
        if int(response['ResponseStatus']) != 0:
            raise ZoozException(
                response['ResponseObject']['errorMessage'],
                response['ResponseStatus'])
        return response
