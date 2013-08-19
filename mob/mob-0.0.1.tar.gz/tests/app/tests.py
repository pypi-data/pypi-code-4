"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.core.urlresolvers import reverse
from django.test import TestCase
from .user_agents import USER_AGENTS
from mob.middleware import MobileDetectorMiddleware, MobileTemplateMiddleware
from django.test.client import Client

def request(ua):
    return type('HttpRequest', (object,), {'META': {'HTTP_USER_AGENT': ua}})()

def response():
    return type('HttpResponse', (object,), {'template_name': ['test_template.html']})()

class UserAgentTest(TestCase):
    def test_mobile_detector_middleware(self):
        detector = MobileDetectorMiddleware()

        for ua in USER_AGENTS:
            req = request(ua)
            detector.process_request(req)
            self.assertTrue(req.is_mobile, ua)

    def test_mobile_template_middleware(self):
        detector = MobileDetectorMiddleware()
        extender = MobileTemplateMiddleware()

        for ua in USER_AGENTS:
            req = request(ua)
            resp = response()

            self.assertEqual(1, len(resp.template_name))
            detector.process_request(req)
            extender.process_template_response(req, resp)

            self.assertEqual(3, len(resp.template_name), resp.template_name)
            self.assertTrue('mobile' in resp.template_name[0])
            self.assertTrue('mobile' in resp.template_name[1])
            self.assertFalse('mobile' in resp.template_name[2])

    def test_mobile_attributes(self):
        detector = MobileDetectorMiddleware()
        iphone, ipod, ipad = map(lambda line: line.strip(), """Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3 like Mac OS X; fr-fr) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8F190 Safari/6533.18.5
		Mozilla/5.0 (iPod; U; CPU iPhone OS 4_2_1 like Mac OS X; he-il) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5
		Mozilla/5.0 (iPad; U; CPU OS 3_2_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B500 Safari/53""".split('\n'))

        req = request(iphone)
        detector.process_request(req)
        self.assertEqual('iphone', req.mobile.slug)

        req = request(ipod)
        detector.process_request(req)
        self.assertEqual('ipod', req.mobile.slug)

        req = request(ipad)
        detector.process_request(req)
        self.assertEqual('ipad', req.mobile.slug)        

    def test_mobile_session_key(self):
        client = Client()
        ua = {'HTTP_USER_AGENT': 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3 like Mac OS X; fr-fr) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8F190 Safari/6533.18.5' }

        resp = client.get('/', **ua)
        self.assertTrue('This is the mobile website.' in resp.content, resp.content)
        
        resp = client.get(reverse('mob:on'), follow=True, **ua)
        self.assertTrue('This is the full website.' in resp.content, resp.content)

        resp = client.get(reverse('mob:off'), follow=True, **ua)
        self.assertTrue('This is the mobile website.' in resp.content, resp.content)

