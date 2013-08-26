# -*- coding: utf8 -*-
from django.test import TestCase
from mobilvest.models import SMSReport
from utils import send_to_gate,get_curl_instance,setup_sms_state,update_sms_state
from lxml import etree

class SendSMSTest(TestCase):
    def test_login(self):
        result = send_to_gate(get_curl_instance(''))
        self.assertTrue(result.replace('\n',''),'<?xml version="1.0" encoding="utf-8"?><response></response>')

    def test_parsers(self):
        sms_answes = (
            ('send', """<?xml version="1.0" encoding="utf-8"?><response><information number_sms="1" id_sms="493478312" parts="1">send</information></response>""",),
            ('error', """<?xml version="1.0" encoding="utf-8"?><response><error>error_text</error></response>"""),
        )
        for unicode_text,result in sms_answes:
            self.assertEqual(unicode_text,setup_sms_state('+79999999999','test_text',result).response_status)


    def test_state_parser(self):
        statuses=("not_deliver","expired","deliver","partly_deliver")
        for status in statuses:
            setup_sms_state('+79999999999','test_text',"""<?xml version="1.0" encoding="utf-8"?><response><information number_sms="1" id_sms="493478312" parts="1">send</information></response>""")
            update_sms_state("""<?xml version="1.0" encoding="utf-8"?><response><state id_sms="493478312" time="2012-12-13 11:21:06" err="000">{status}</state></response>""".format(status=status))
            sms = SMSReport.objects.get(sms_id=493478312)
            self.assertEqual(sms.response_status,status)
            sms.delete()
