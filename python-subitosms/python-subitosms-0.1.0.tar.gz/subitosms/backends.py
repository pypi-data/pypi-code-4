# -*- coding: iso-8859-1 -*-


from .gateways import JsonGatewaySubitoSms, PhpGatewaySubitoSms

try:
    from django.conf import settings

    SUBITOSMS_USERNAME = settings.SUBITOSMS_USERNAME
    SUBITOSMS_PASSWORD = settings.SUBITOSMS_PASSWORD
except ImportError:
    SUBITOSMS_USERNAME = ''
    SUBITOSMS_PASSWORD = ''


class JsonSubitoSmsBacked(object):

    def send(self, **data):
        if 'number_to' not in data.keys() or 'text' not in data.keys():
            raise TypeError("send() takes at least number_to and text"
                            " key arguments")
        if data['number_to'] is None or data['text'] is None:
            raise ValueError("send() takes number_to and text key arguments"
                             " not None.")
        test = False
        if 'sender' not in data.keys():
            data.update({'sender': ''})
        if 'sending_test' in data.keys() and data['sending_test'] is True:
            test = True
            data['sender'] = data['sender'].zfill(30)

        gateway = JsonGatewaySubitoSms(username=SUBITOSMS_USERNAME,
                                       password=SUBITOSMS_PASSWORD)
        result = gateway.send_sms(data['number_to'],
                                  data['text'],
                                  sender=data['sender'])
        return result['data']['id']


class PhpSubitoSmsBacked(object):

    def send(self, **data):
        if 'number_to' not in data.keys() or 'text' not in data.keys():
            raise TypeError("send() takes at least number_to and text"
                            " key arguments")
        if data['number_to'] is None or data['text'] is None:
            raise ValueError("send() takes number_to and text key arguments"
                             " not None.")
        test = False
        if 'sender' not in data.keys():
            data.update({'sender': ''})
        if 'sending_test' in data.keys() and data['sending_test'] is True:
            test = True

        gateway = PhpGatewaySubitoSms(username=SUBITOSMS_USERNAME,
                                      password=SUBITOSMS_PASSWORD,
                                      test=test)
        result = gateway.send_sms(data['number_to'],
                                  data['text'],
                                  sender=data['sender'])
        return result['id']


