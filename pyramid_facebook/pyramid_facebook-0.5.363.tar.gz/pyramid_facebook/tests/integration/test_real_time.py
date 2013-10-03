import json
import hashlib
import hmac

import mock
from pyramid.config import Configurator
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPForbidden
from webtest import TestApp


class Mixin(object):

    @reify
    def config(self):
        self.addCleanup(delattr, self, 'config')
        return Configurator(settings={})

    @reify
    def app(self):
        self.addCleanup(delattr, self, 'app')
        return TestApp(self.config.make_wsgi_app())

    @property
    def real_time_path(self):
        return ('/%s/real-time' %
                self.config.registry.settings['facebook.namespace'])

    def sign(self, body):
        secret_key = self.config.registry.settings['facebook.secret_key']
        return "sha1=%s" % hmac.new(secret_key, body, hashlib.sha1).hexdigest()

    def get_update_dict(self):
        return {
            "object": "user",
            "entry": [
                {"uid": 111,
                 "changed_fields": ["name", "picture"],
                 "time": 123456,
                 },
                {"uid": 222,
                 "changed_fields": ["friends"],
                 "time": 123456,
                 },
                ]
            }

    def test_real_time_update_invalid_signature(self):
        with self.assertRaises(HTTPForbidden):
            self.app.post(
                self.real_time_path,
                headers={
                    'X-Hub-Signature': 'invalid signature',
                    'Content-Type': 'application/json',
                    }
                )

    def test_real_time_update(self):
        from pyramid_facebook.events import ChangeNotification
        json_body = json.dumps(self.get_update_dict())

        rt_subscriber = mock.Mock()
        self.config.add_subscriber(rt_subscriber, ChangeNotification)

        self.app.post(
            self.real_time_path,
            json_body,
            headers={
                'X-Hub-Signature': self.sign(json_body),
                'Content-Type': 'application/json',
                }
            )

        self.assertEqual(1, len(rt_subscriber.call_args_list))
        event = rt_subscriber.call_args_list[0][0][0]

        self.assertEqual(self.get_update_dict(), event.json_body)
