# -*- coding: utf-8 -*-

import json
import logging
# import urllib
try:
    from urllib import urlencode
    from urllib2 import Request, urlopen
except ImportError:
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen


logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class JsonGatewayException(Exception):
    def __init__(self, dict_error):
        self.dict_error = dict_error
        self.message = self.dict_error['error']['message']
        self.code = self.dict_error['error']['code']

    def __str__(self):
        return repr(self.dict_error)

    def __repr__(self):
        return 'ValidationError({})'.format(repr(self.dict_error))


class GatewaySubitoSms(object):

    def __init__(self, username=None, password=None, test=True):
        self._username = username
        self._password = password
        self.test = test

    def set_auth(self, username, password):
        self._username = username
        self._password = password

    def check_credit(self):
        """Return credits information"""
        raise NotImplementedError

    def remaining_sms_credit(self):
        """Return number of remaining sms"""
        raise NotImplementedError

    def send_bulk_sms(self, dests, text, sender=''):
        """Sends a group (bulk) of messages"""
        raise NotImplementedError

    def send_sms(self, dest, text, sender=''):
        """Sends a single message"""
        raise NotImplementedError

    def check_status(self, ids):
        """Return messages status information"""
        raise NotImplementedError

    def is_sent(self, id_sms):
        """Return true if the message has been sent successfully"""
        raise NotImplementedError

    @classmethod
    def get_verbose_status(cls, code):
        code = str(code)
        if code == '8':
            return 'Sent'
        if code == '-100':
            return 'Gateway error'
        if code == '-50':
            return 'Destination has been blocked'
        if code == '-2':
            return 'Not processed'
        if code == '-1':
            return 'Not processed'
        if code == '0':
            return 'Accepted by gateway'
        if code == '1':
            return 'Delivered to phone'
        if code == '2':
            return 'Not delivered to phone'
        if code == '4':
            return 'Buffered'
        if code == '16':
            return 'Refused'
        return 'Unknown code.'


class JsonGatewaySubitoSms(GatewaySubitoSms):

    _url = 'https://www.subitosms.it/json.php'

    def __init__(self, username=None, password=None, test=True):
        super(JsonGatewaySubitoSms, self).__init__(username=username,
                                                   password=password,
                                                   test=test)

    def get_auth_data(self):
        result = {'auth': {'username': self._username,
                           'password': self._password}}
        return result

    def prepare_data(self, data=None):
        result = self.get_auth_data()
        if data is None:
            result.update({'data': []})
        else:
            result.update({'data': data})
        return json.dumps(result)

    def make_request(self, action='credit', data=None):
        url = '{}?action={}'.format(self._url, action)
        if self.test:
            url += '&test=1'
        data = self.prepare_data(data=data)
        logging.debug('make_request: {} ({})'.format(url, data))
        req = Request(url, data.encode('utf8'))
        response = urlopen(req).read()
        result = json.loads(response)
        if 'error' in result:
            raise JsonGatewayException(result)
        return result

    def check_credit(self):
        """Return credits information"""
        return self.make_request(action='credit')

    def remaining_sms_credit(self):
        """Return number of remaining sms"""
        result = self.check_credit()
        return int(result['data']['Italy'])

    def send_bulk_template_sms(self, dests, text, sender=''):
        """Sends a group (bulk) of messages"""
        if type(dests) is not list:
            data = [{'sender': sender, 'dest': dests, 'text': text}]
        else:
            data = list([{'sender': sender,
                          'dest': dest,
                          'text': text} for dest in dests])
        return self.make_request(action='send', data=data)

    def send_sms(self, dest, text, sender=''):
        """Sends a single message"""
        data = [{'sender': sender, 'dest': dest, 'text': text}]
        return self.make_request(action='send', data=data)

    def check_status(self, ids):
        """Return messages status information"""
        if type(ids) is not list:
            data = [{'id': int(ids)}]
        else:
            data = list([{'id': int(item)} for item in ids])
        return self.make_request(action='status', data=data)


class PhpGatewaySubitoSms(GatewaySubitoSms):

    _url = 'https://www.subitosms.it/gateway.php'

    def get_auth_data(self):
        return {'username': self._username,
                'password': self._password}

    def prepare_data(self, dest=None, text=None, sender=None, ids=None):
        data = self.get_auth_data()
        if dest is None and text is None and sender is None:
            if ids is not None:
                data.update({'id': str(ids)})
            return data
        data.update({'testo': text, 'mitt': sender})
        if type(dest) is not list:
            data.update({'dest': dest})
        else:
            dest = [str(d) for d in dest]
            data.update({'dest': ','.join(dest)})
        return data

    def make_request(self, data=None):
        url = self._url + '?'
        if self.test:
            url += '&test=1'
        if data is None:
            data = self.prepare_data()
        for k in data:
            data[k] = data[k].encode('utf-8')
        logging.debug('make_request: {} ({})'.format(url, data))
        req = Request(url, data.encode('utf8'))
        response = urlopen(req)
        return response.read()

    def check_credit(self):
        """Return credits information"""
        result = str(self.make_request()).strip()
        return result

    def remaining_sms_credit(self):
        """Return number of remaining sms"""
        result = str(self.check_credit())
        if result.find('credito') == -1:
            return False
        return int(result.split(':')[1])

    def send_bulk_template_sms(self, dests, text, sender=''):
        """Sends a group (bulk) of messages"""
        return self.send_sms(dests, text, sender)

    def send_sms(self, dest, text, sender=''):
        """Sends a single message"""
        result = self.make_request(
            data=self.prepare_data(dest=dest, text=text, sender=sender))
        if result.find('id') == -1:
            return False
        return {'id': result.strip().split(':')[1]}

    def check_status(self, ids):
        """Return messages status information"""
        result = self.make_request(data=self.prepare_data(ids=ids))
        return [dict(d) for d in
                [[x.split(':') for x in s.strip(' \r').split(';')]
                 for s in result.split('\n') if s != '']]