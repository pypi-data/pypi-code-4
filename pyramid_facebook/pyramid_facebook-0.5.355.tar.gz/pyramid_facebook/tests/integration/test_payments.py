import json
import hashlib
import hmac
from decimal import Decimal

import mock
from facepy import FacepyError
from pyramid.config import Configurator
from pyramid.decorator import reify
from webtest import TestApp

from . import JSONEncoder


class Mixin(object):
    """A mixin integratiom test for real-time update on payments.
    """
    user_id = 700
    application_id = 2222
    virtual_good_id = 1

    @reify
    def config(self):
        self.addCleanup(delattr, self, 'config')
        return Configurator(settings={})

    @reify
    def app(self):
        self.addCleanup(delattr, self, 'app')
        return TestApp(self.config.make_wsgi_app())

    @property
    def namespace(self):
        return self.config.registry.settings['facebook.namespace']

    @property
    def real_time_path(self):
        return ('/%s/real-time' % self.namespace)

    def sign(self, body):
        secret_key = self.config.registry.settings['facebook.secret_key']
        return "sha1=%s" % hmac.new(secret_key, body, hashlib.sha1).hexdigest()

    def get_payment_dict(self):
        return {
            u'actions': [{
                u'amount': u'39.99',
                u'currency': u'EUR',
                u'status': u'completed',
                u'time_created': u'2013-08-08T21:19:59+0000',
                u'time_updated': u'2013-08-08T21:19:59+0000',
                u'type': u'charge',
                }],
            u'application': {
                u'id': self.application_id,
                u'name': u'TEST',
                u'namespace': u'%s' % self.namespace
                },
            u'country': u'CA',
            u'created_time': u'2013-08-08T21:19:59+0000',
            u'id': u'111',
            u'items': [{
                u'product': u'http://example.com/%s/item/%s' % (
                    self.namespace,
                    self.virtual_good_id,
                    ),
                u'quantity': 1,
                u'type': u'IN_APP_PURCHASE',
                }],
            u'payout_foreign_exchange_rate': Decimal('1.3131459'),
            u'refundable_amount': {u'amount': u'39.99', u'currency': u'EUR'},
            u'test': 1,
            u'user': {
                u'id': self.user_id,
                u'name': u'Joe Manix'
                }
            }

    def get_notification_dict(self):
        return {
            u'object': u'payments',
            u'entry': [{
                u'id': u'111',
                u'time': 1347996346,
                u'changed_fields': ['actions']
                }]
            }

    @mock.patch('pyramid_facebook.utility.get_application_graph_api')
    def test_real_time_payment_update_completed(self, m_get_graph_api):
        from pyramid_facebook.events import OrderReceived
        json_body = json.dumps(self.get_notification_dict())

        or_subscriber = mock.Mock()
        self.config.add_subscriber(or_subscriber, OrderReceived)

        payment = self.get_payment_dict()

        batch_results = [{u'body': json.dumps(payment, cls=JSONEncoder)}]

        m_graph_api = m_get_graph_api.return_value
        m_graph_api.post.return_value = batch_results

        self.app.post(
            self.real_time_path,
            json_body,
            headers={
                'X-Hub-Signature': self.sign(json_body),
                'Content-Type': 'application/json',
                }
            )

        self.assertEqual(1, len(or_subscriber.call_args_list))
        event = or_subscriber.call_args_list[0][0][0]

        self.assertEqual(payment, event.payment)

    @mock.patch('pyramid_facebook.utility.get_application_graph_api')
    def test_real_time_payment_update_failed(self, m_get_graph_api):
        from pyramid_facebook.events import OrderReceived
        json_body = json.dumps(self.get_notification_dict())

        or_subscriber = mock.Mock()
        self.config.add_subscriber(or_subscriber, OrderReceived)

        payment = self.get_payment_dict()
        payment['actions'][0]['status'] = 'failed'

        batch_results = [{u'body': json.dumps(payment, cls=JSONEncoder)}]

        m_graph_api = m_get_graph_api.return_value
        m_graph_api.post.return_value = batch_results

        self.app.post(
            self.real_time_path,
            json_body,
            headers={
                'X-Hub-Signature': self.sign(json_body),
                'Content-Type': 'application/json',
                }
            )

        self.assertEqual(1, len(or_subscriber.call_args_list))
        event = or_subscriber.call_args_list[0][0][0]

        self.assertEqual(payment, event.payment)

    @mock.patch('pyramid_facebook.utility.get_application_graph_api')
    def test_real_time_payment_with_facebook_fail(self, m_get_graph_api):
        from pyramid_facebook.events import OrderReceived
        json_body = json.dumps(self.get_notification_dict())

        or_subscriber = mock.Mock()
        self.config.add_subscriber(or_subscriber, OrderReceived)

        m_graph_api = m_get_graph_api.return_value
        m_graph_api.post.side_effect = FacepyError('shit hits the fan')

        self.app.post(
            self.real_time_path,
            json_body,
            headers={
                'X-Hub-Signature': self.sign(json_body),
                'Content-Type': 'application/json',
                },
            status=500,
            )

        self.assertEqual(0, or_subscriber.call_count)

    @mock.patch('pyramid_facebook.utility.get_application_graph_api')
    def test_real_time_payment_fb_batch_response_invalid(self,
                                                         m_get_graph_api):
        from pyramid_facebook.events import OrderReceived
        json_body = json.dumps(self.get_notification_dict())

        or_subscriber = mock.Mock()
        self.config.add_subscriber(or_subscriber, OrderReceived)

        batch_results = [{u'body': 'not a valid json body'}]

        m_graph_api = m_get_graph_api.return_value
        m_graph_api.post.return_value = batch_results

        self.app.post(
            self.real_time_path,
            json_body,
            headers={
                'X-Hub-Signature': self.sign(json_body),
                'Content-Type': 'application/json',
                },
            status=500
            )

        self.assertEqual(0, len(or_subscriber.call_args_list))
