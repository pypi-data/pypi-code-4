import logging
from decimal import Decimal

import requests
from facepy import SignedRequest
from facepy.utils import get_application_access_token
from facepy.signed_request import SignedRequestError
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest, HTTPServerError

from pyramid_facebook.events import OrderCreated, OrderCreationError

log = logging.getLogger(__name__)


def includeme(config):
    """Add views related to local currency payments."""
    config.add_route('facebook_payments_order',
                     'orders/{order_id}')
    config.scan('.payments')


@view_config(route_name='facebook_payments_order',
             request_method='PUT',
             request_param='signed_request',
             renderer='string')
def put_order(context, request):
    """Use this view as server-side verification method.

    If you want to verify payments and maybe update user
    info on the backend side, write a client-side callback
    that sends the payment's signed request data (effectively
    keeping the old model of a blocking credits callback
    instead of using a real-time update handler).

    This view checks the payment using the Graph API and
    sends an OrderCreated event.  If a subscriber raises an
    exception, it is logged, OrderCreationError is sent (an
    exception in one of its subscribers will also be logged),
    and HTTPServerError is raised.  An event subscriber doing
    something non-critical like tracking should catch all its
    exceptions, otherwise the client code will think the order
    was not processed.

    If the signed request is invalid, or if the payment ID in
    the signed request does not match the current URI,
    HTTPBadRequest will be raised and no event will be sent.
    This indicates a configuration or application bug; the
    error will be logged to aid debugging and refunding.

    See https://developers.facebook.com/docs/howtos/payments/fulfillment/
    """
    signed_request = request.POST['signed_request']
    app_id = request.registry.settings['facebook.app_id']
    secret_key = request.registry.settings['facebook.secret_key']
    try:
        signed_request = SignedRequest.parse(signed_request,
                                             secret_key)
    except SignedRequestError as exc:
        log.exception('invalid signed request')
        raise HTTPBadRequest(exc)

    payment_id = unicode(signed_request['payment_id'])
    if payment_id != request.matchdict['order_id']:
        log.error(
            'mismatch between order_id=%r in URI and payment_id=%r in'
            ' signed request', request.matchdict['order_id'], payment_id)
        raise HTTPBadRequest('invalid payment ID')

    token = get_application_access_token(app_id, secret_key)
    # TODO use facepy.GraphAPI when the fix for Decimal is released
    # https://github.com/jgorset/facepy/issues/86
    payment = requests.get('https://graph.facebook.com/' + payment_id,
                           params={'access_token': token})
    payment = payment.json(parse_float=Decimal)

    try:
        request.registry.notify(OrderCreated(request, payment))
    except Exception:
        log.exception('error during order creation payment=%r', payment)
        try:
            request.registry.notify(OrderCreationError(request, payment))
        except Exception:
            log.critical('error during notification of order creation error',
                         exc_info=True)
        raise HTTPServerError()
