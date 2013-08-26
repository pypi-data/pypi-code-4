import os
import hmac
import logging

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest, HTTPServerError

from . import _request_params


log = logging.getLogger(__name__)


def includeme(config):
    """Define resources and views for TrialPay Offerwall.

    Doc: http://help.trialpay.com/facebook/offer-wall/

    OpenGraph objects for the currencies are not defined by this
    module, you should use a library like pyramid_facebook.
    """
    app_id = config.registry.settings['facebook.app_id']
    # TODO should check for envvars here
    params_predicate = _request_params(
        'sid',
        'oid',
        'reward_amount',
        'currency_url',
        'order_info',
        'callback_url',
        app_id=app_id,
    )
    config.add_route('game_offers_trialpay_offerwall_callback',
                     '/game_offers/trialpay/offerwall',
                     request_method='POST',
                     header='TrialPay-HMAC-MD5',
                     custom_predicates=[params_predicate])
    config.scan(__name__)


class CurrencyEarned(object):
    """Event sent for validated orders.

    All constructor parameters are set as instance attributes.
    """

    def __init__(self, request, transaction_id, third_party_id,
                 currency_url, currency_amount, order_info):
        self.request = request
        self.transaction_id = transaction_id
        self.third_party_id = third_party_id
        self.currency_url = currency_url
        self.currency_amount = currency_amount
        self.order_info = order_info


@view_config(route_name='game_offers_trialpay_offerwall_callback',
             renderer='string')
def validate_order(context, request):
    """Validate TrialPay request and send CurrencyEarned event.

    Returns HTTP 200 with response body "1" for success.

    Raises HTTP 400 for invalid requests, HTTP 500 if an
    event subscriber raises an exception.
    """
    key = os.environ['GAMEOFFERS_TRIALPAY_MERCHANT_KEY']
    checksum = hmac.new(key, request.body).hexdigest()
    provided_checksum = request.headers['TrialPay-HMAC-MD5']
    if checksum != provided_checksum:
        request.response.status_code = HTTPBadRequest.code
        return 'Invalid request.'

    event = CurrencyEarned(request,
                           request.params['oid'],
                           request.params['sid'],
                           request.params['currency_url'],
                           request.params['reward_amount'],
                           request.params['order_info'])
    log.debug(
        'currency earned transaction_id=%s third_party_id=%s '
        'currency_url=%s currency_amount=%s order_info=%s',
        event.transaction_id, event.third_party_id,
        event.currency_url, event.currency_amount, event.order_info)

    try:
        request.registry.notify(event)
        # Success!
        return '1'
    except Exception:
        log.exception('error while notifying CurrencyEarned')
        request.response.status_code = HTTPServerError.code
        return 'Server error.'
