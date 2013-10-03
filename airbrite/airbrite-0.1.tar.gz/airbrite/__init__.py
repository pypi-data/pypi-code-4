import requests
import json
import api

END_POINT = 'https://api.airbrite.io/v2/'
TEST_API_KEY = 'sk_test_a805be8b2add854f09976b3b5c0f5bd06c14617c'

# Initialize to the test API key and password
API_KEY = TEST_API_KEY
API_KEY_PASSWORD = ''


import logging
logger = logging.getLogger('airbrite')


def _get(resource):
    logger.debug('REST API call - _get(%s)' % resource)
    return requests.get(END_POINT + resource, auth=(API_KEY, API_KEY_PASSWORD))


def _post(resource, data={}):
    url = END_POINT + resource
    headers = {'content-type': 'application/json'}
    payload = json.dumps(data)
    logger.debug('REST API call - _post(%s)' % resource)
    return requests.post(url, auth=(API_KEY, API_KEY_PASSWORD),
                         headers=headers, data=payload)


def test_connection():
    """Returns True if the API is operational, False otherwise"""
    # TODO: implement a cheaper test

    # Connection test based on assumption that the test API key is used, and
    # that there's at least one product registered.
    result = _get('products')
    if result.status_code == 200:
        return True
    return False


###############################################################################

def get_product(product_id):
    """Returns an api.Product object for the provided ID"""

    response = _get('products/' + product_id)
    if response.status_code != 200:
        error_msg = response.json()['data']
        logger.error('get_product() failed with "%s"' % error_msg)
        raise Exception('Product not found')
    product_data = response.json()[u'data']
    return api.Product(product_data)


def get_products():
    """Returns an iterable of api.Product objects"""

    response = _get('products')
    if response.status_code != 200:
        error_msg = response.json()['data']
        logger.error('get_products() failed with "%s"' % error_msg)
        # TODO: make this a critical error
        raise Exception('Products endpoint failed')

    # TODO: adapt to pagination
    data = response.json()
    for product_data in data[u'data']:
        yield api.Product(product_data)


###############################################################################

def payment(card_token='', amount=0, gateway="stripe", currency="usd"):
    """Helper function that returns a payment dict."""
    if not card_token or not amount:
        raise ValueError("Arguments `amount` and `card_token` are required")
    if amount < 50:
        raise ValueError("Amount must be an integer greater than 50c")
    return {
        'gateway': gateway,
        'currency': currency,
        'amount': amount,
        'card_token': card_token,
    }


def new_order(sku='', quantity=0, line_items=[], payments=[]):
    # TODO: Generalize the payload generation
    if sku and quantity:
        payload = {
            "line_items": [{
                "sku": sku,
                "quantity": quantity,
            }]
        }
    elif line_items:
        payload = {
            "line_items": line_items,
        }
    else:
        raise ValueError('Either sku+quantity or line_items must be specifed')

    # Add payments to the payload, if specified
    if payments:
        payload['payments'] = payments

    response = _post('orders', data=payload)
    if response.status_code != 200:
        error_msg = response.json()['data']
        logger.error('new_order() failed with "%s"' % error_msg)
        raise Exception('Order could not be placed')

    return api.Order(response.json()['data'])
