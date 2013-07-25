"""
run this with ./manage.py test website
see http://www.djangoproject.com/documentation/testing/ for details
"""
import os
from django.conf import settings
from django.shortcuts import render_to_response
from django.test import TestCase
from django_moip.html.redirector.forms import MoipRedirectorForm
from django_moip.html.redirector.models import MoipRedirector
from django_moip.html.redirector.signals import redirector_successful, redirector_failed


class DummyMoipRedirector(object):
    
    def __init__(self, update_context_dict={}):
        self.context_dict = {'st': 'SUCCESS', 'custom':'cb736658-3aad-4694-956f-d0aeade80194',
                             'txn_id':'1ED550410S3402306', 'mc_gross': '225.00', 
                             'business': settings.MOIP_RECEIVER_EMAIL, 'error': 'Error code: 1234'}
        
        self.context_dict.update(update_context_dict)
        self.response = ''
        
    def update_with_get_params(self, get_params):
        if get_params.has_key('tx'):
            self.context_dict['txn_id'] = get_params.get('tx')
        if get_params.has_key('amt'):
            self.context_dict['mc_gross'] = get_params.get('amt')
        if get_params.has_key('cm'):
            self.context_dict['custom'] = get_params.get('cm')
            
    def _postback(self, test=True):
        """Perform a Fake MoIP Redirector Postback request."""
        # @@@ would be cool if this could live in the test templates dir...
        return render_to_response("pdt/test_redirector_response.html", self.context_dict).content

class RedirectorTest(TestCase):
    urls = "django_moip.html.redirector.tests.test_urls"
    template_dirs = [os.path.join(os.path.dirname(__file__), 'templates'),]

    def setUp(self):
        # set up some dummy Redirector get parameters
        self.get_params = {"tx":"4WJ86550014687441", "st":"Completed", "amt":"225.00", "cc":"EUR",
                      "cm":"a3e192b8-8fea-4a86-b2e8-d5bf502e36be", "item_number":"",
                      "sig":"blahblahblah"}
        
        # monkey patch the MoipRedirector._postback function
        self.dpppdt = DummyMoipRedirector()
        self.dpppdt.update_with_get_params(self.get_params)
        MoipRedirector._postback = self.dpppdt._postback

    def test_verify_postback(self):
        dpppdt = DummyMoipRedirector()
        moip_response = dpppdt._postback()
        assert('SUCCESS' in moip_response)
        self.assertEqual(len(MoipRedirector.objects.all()), 0)
        redirector_obj = MoipRedirector()
        redirector_obj.ipaddress = '127.0.0.1'
        redirector_obj.response = moip_response
        redirector_obj._verify_postback()
        self.assertEqual(len(MoipRedirector.objects.all()), 0)
        self.assertEqual(redirector_obj.txn_id, '1ED550410S3402306')
        
    def test_pdt(self):        
        self.assertEqual(len(MoipRedirector.objects.all()), 0)        
        self.dpppdt.update_with_get_params(self.get_params)
        moip_response = self.client.get("/pdt/", self.get_params)        
        self.assertContains(moip_response, 'Transaction complete', status_code=200)
        self.assertEqual(len(MoipRedirector.objects.all()), 1)

    def test_redirector_signals(self):
        self.successful_redirector_fired = False        
        self.failed_redirector_fired = False
        
        def successful_pdt(sender, **kwargs):
            self.successful_redirector_fired = True
        redirector_successful.connect(successful_pdt)
            
        def failed_pdt(sender, **kwargs):
            self.failed_redirector_fired = True 
        redirector_failed.connect(failed_pdt)
        
        self.assertEqual(len(MoipRedirector.objects.all()), 0)        
        moip_response = self.client.get("/pdt/", self.get_params)
        self.assertContains(moip_response, 'Transaction complete', status_code=200)        
        self.assertEqual(len(MoipRedirector.objects.all()), 1)
        self.assertTrue(self.successful_redirector_fired)
        self.assertFalse(self.failed_redirector_fired)        
        redirector_obj = MoipRedirector.objects.all()[0]
        self.assertEqual(redirector_obj.flag, False)
        
    def test_double_redirector_get(self):
        self.assertEqual(len(MoipRedirector.objects.all()), 0)            
        moip_response = self.client.get("/pdt/", self.get_params)
        self.assertContains(moip_response, 'Transaction complete', status_code=200)
        self.assertEqual(len(MoipRedirector.objects.all()), 1)
        redirector_obj = MoipRedirector.objects.all()[0]        
        self.assertEqual(redirector_obj.flag, False)        
        moip_response = self.client.get("/pdt/", self.get_params)
        self.assertContains(moip_response, 'Transaction complete', status_code=200)
        self.assertEqual(len(MoipRedirector.objects.all()), 1) # we don't create a new pdt        
        redirector_obj = MoipRedirector.objects.all()[0]
        self.assertEqual(redirector_obj.flag, False)

    def test_no_txn_id_in_pdt(self):
        self.dpppdt.context_dict.pop('txn_id')
        self.get_params={}
        moip_response = self.client.get("/pdt/", self.get_params)
        self.assertContains(moip_response, 'Transaction Failed', status_code=200)
        self.assertEqual(len(MoipRedirector.objects.all()), 0)
        
    def test_custom_passthrough(self):
        self.assertEqual(len(MoipRedirector.objects.all()), 0)        
        self.dpppdt.update_with_get_params(self.get_params)
        moip_response = self.client.get("/pdt/", self.get_params)
        self.assertContains(moip_response, 'Transaction complete', status_code=200)
        self.assertEqual(len(MoipRedirector.objects.all()), 1)
        redirector_obj = MoipRedirector.objects.all()[0]
        self.assertEqual(redirector_obj.custom, self.get_params['cm'] )