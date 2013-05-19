#-*- coding:utf-8 -*-
import urllib2

from django.conf import settings


def send(phone, message):
    url = 'http://sms.ru/sms/send?api_id={0}&to={1}&text={2}'.format(settings.SMS_RU_APT_ID, phone, message)
    try:
        urllib2.urlopen(url).read()
    except:
        pass
