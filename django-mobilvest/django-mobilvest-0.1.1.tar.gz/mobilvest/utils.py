# -*- coding: utf8 -*-
import pycurl
import datetime
from lxml import etree
from models import SMSTemplate,SMSReport
import settings

__author__ = 'ir4y'

def get_curl_instance(body,action='default'):
    src='<?xml version="1.0" encoding="utf-8"?><request><security><login value="{login}" /><password value="{password}" /></security>{body}</request>'
    curl = pycurl.Curl()
    curl.setopt(pycurl.HTTPHEADER, ['Content-type: text/xml; charset=utf-8'])
    curl.setopt(pycurl.CRLF, True)
    curl.setopt(pycurl.POST, True)
    curl.setopt(pycurl.POSTFIELDS, src.format(login=settings.USER,password=settings.PASSWORD,body=body))
    url = {'default':settings.SEND_GATE,'satus':settings.STATUS_GATE}[action]
    curl.setopt(pycurl.URL, url)
    return curl

def send_to_gate(curl):
    result = []
    curl.setopt(pycurl.WRITEFUNCTION, lambda chunk:result.append(chunk))
    curl.setopt(pycurl.FOLLOWLOCATION, 1)
    curl.setopt(pycurl.MAXREDIRS, 5)
    curl.perform()
    curl.close()
    return ''.join(result)

def send_sms_from_template(sms_template_pk,extra_context={}):
    template=SMSTemplate.objects.get(pk=sms_template_pk).text
    context={'datetime':datetime.datetime.now()}
    context.update(extra_context)
    send_to_gate(template.format(context))

def get_xml_body(message_text,phone):
    message = etree.Element("message",type="sms")

    sender = etree.Element("sender")
    sender.text = settings.SENDER
    message.append(sender)

    text = etree.Element("text")
    text.text=message_text
    message.append(text)

    abonent = etree.Element("abonent",phone=phone,number_sms="1")
    message.append(abonent)

    return etree.tostring(message)

def setup_sms_state(phone,text,result):
    parse_result = etree.fromstring(result)
    main_tag = parse_result[0]
    if main_tag.tag == 'information':
        return SMSReport.objects.create(sms_id=main_tag.attrib['id_sms'],response_status='send',mobile_phone=phone,text=text)
    elif main_tag.tag == 'error':
        return SMSReport.objects.create(response_status='error',mobile_phone=phone,text=text,error=main_tag.text)

def get_sended_sms_xml():
    get_state = etree.Element("get_state")
    count = 0
    for sms in SMSReport.objects.filter(response_status='send'):
        count += 1
        id_sms = etree.Element("id_sms")
        id_sms.text = "%d" % sms.sms_id
        get_state.append(id_sms)
    return etree.tostring(get_state),count

def update_sms_state(result):
    main_tag = etree.fromstring(result)
    if main_tag.tag == 'response':
        for state in main_tag:
            sms = SMSReport.objects.get(sms_id=state.attrib['id_sms'])
            sms.response_status = state.text
            sms.save()
