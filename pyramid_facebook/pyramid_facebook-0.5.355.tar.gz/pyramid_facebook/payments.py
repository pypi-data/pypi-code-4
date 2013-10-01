import json
import logging
from decimal import Decimal

import requests
from facepy import SignedRequest, FacepyError
from facepy.utils import get_application_access_token
from facepy.signed_request import SignedRequestError
from pyramid.events import subscriber
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPFailedDependency,
    HTTPServerError,
)
from pyramid.view import view_config

from pyramid_facebook.events import (
    OrderReceived,
    OrderProcessingError,
    ChangeNotification,
)

log = logging.getLogger(__name__)


def includeme(config):
    """Add views related to local currency payments."""
    config.include('pyramid_facebook.predicates')
    config.include('pyramid_facebook.utility')
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
    sends an OrderReceived event.  If a subscriber raises an
    exception, it is logged, OrderProcessingError is sent (an
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

    notify_order_received(request, payment)


@subscriber(ChangeNotification, update_object='payments')
def process_payments(event):
    request = event.request
    entries = request.json_body['entry']
    batch = [{'relative_url': entry['id'], 'method': 'GET'}
             for entry in entries]
    log.debug('Posting batch batch=%s', batch)
    try:
        results = request.graph_api.post('/', batch=json.dumps(batch))
    except FacepyError:
        log.exception('Batch request failed. json_body=%s', request.json_body)
        raise HTTPFailedDependency('Facebook batch request failed')

    for result in results:
        try:
            payment = json.loads(result['body'], parse_float=Decimal)
        except (KeyError, ValueError):
            log.exception('Facebook batch response invalid: results=%s',
                          results)
            raise HTTPFailedDependency('Facebook batch response invalid')

        notify_order_received(request, payment)


def notify_order_received(request, payment):
    log.debug('notifying OrderReceived: payment=%s', payment)
    try:
        request.registry.notify(OrderReceived(request, payment))
    except Exception:
        log.exception(
            u'notifying OrderReceived: user_id=%s, order_id=%s, actions=%s',
            payment[u'user'][u'id'],
            payment[u'id'],
            payment[u'actions'],
        )
        try:
            request.registry.notify(OrderProcessingError(request, payment))
        except Exception:
            log.critical(
                u'notifying OrderProcessingError:  user_id=%s, order_id=%s '
                u'actions=%s',
                payment[u'user'][u'id'],
                payment[u'id'],
                payment[u'actions'],
                exc_info=True,
            )
        raise HTTPServerError()
