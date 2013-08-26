# -*- coding: utf8 -*-
from celery.task import task
from utils import *
__author__ = 'ir4y'

@task
def send_sms(phone,sms_template_pk,extra_context={}):
    text = send_sms_from_template(sms_template_pk,extra_context)
    send_raw_sms(phone,text)

@task
def send_raw_sms(phone,text):
    result = send_to_gate(get_curl_instance(get_xml_body(text,phone)))
    setup_sms_state(phone,text,result)
    print(phone,result)

@task
def get_sms_status():
    xml,count = get_sended_sms_xml()
    if count == 0:
        return
    result = send_to_gate(get_curl_instance(xml,'satus'))
    update_sms_state(result)
    print(result)
