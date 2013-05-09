#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
import tuisongbao.utils as utils

FORMAT = 'json'
API_VERSION = '1.0'
BASE_URL = 'http://rest.tuisongbao.com'
NOTIFICATION_URL = '/notification'


class Client(object):
    def __init__(self, apikey, apisecret):
        self.sysParams = {}
        self.sysParams['apikey'] = apikey
        self.sysParams['apisecret'] = apisecret
        self.sysParams['format'] = FORMAT
        self.sysParams['v'] = API_VERSION

    def send_notification_to_all(self, appkey, message, options={}):
        options['appkey'] = appkey
        options['message'] = message

        return self._send_notification(options)

    def send_notification_by_tokens(self, appkey, tokens, message, options={}):
        options['appkey'] = appkey
        options['tokens'] = tokens
        options['message'] = message

        return self._send_notification(options)

    def send_notification_by_channels(self, appkey, channels, message, options={}):
        options['appkey'] = appkey
        options['channels'] = channels
        options['message'] = message

        return self._send_notification(options)

    def send_notification_by_appversion(self, appkey, appv, message, options={}):
        options['appkey'] = appkey
        options['appv'] = appv
        options['message'] = message

        return self._send_notification(options)

    def send_notification_by_channels_and_appversion(self, appkey, channels, appv, message, options={}):
        options['appkey'] = appkey
        options['channels'] = channels
        options['appv'] = appv
        options['message'] = message

        return self._send_notification(options)

    def _send_notification(self, options):
        if 'est' in options:
            options['est'] = utils.formatDatetime(options['est'])

        params = {}
        params.update(options)
        params.update(self.sysParams)
        del params['apisecret']

        params_to_sign = {}
        params_to_sign.update(self.sysParams)
        del params_to_sign['apisecret']
        params_to_sign['appkey'] = options['appkey']
        params_to_sign['message'] = options['message']
        if 'est' in options:
            params_to_sign['est'] = options['est']

        result = self._request(BASE_URL + NOTIFICATION_URL, params, params_to_sign, False)

        return result['nid']

    def query_notification_status(self, appkey, nid):
        params = {'appkey': appkey}
        params.update(self.sysParams)
        del params['apisecret']

        result = self._request(BASE_URL + NOTIFICATION_URL + '/' + str(nid), params, params)

        return {'success': result['success'], 'failed': result['failed']}

    def _request(self, url, params, params_to_sign, get=True):
        params['timestamp'] = params_to_sign['timestamp'] = utils.formatDatetime()
        params['sign'] = utils.md5_sign(params_to_sign, self.sysParams['apisecret'])

        if get:
            r = requests.get(url, params=params)
        else:
            headers = {'content-type': 'application/json'}
            r = requests.post(url, data=json.dumps(params), headers=headers)

        if r.status_code != 200:
            raise TuisongbaoError('http request failed, statusCode: ' + r.status_code)

        try:
            result = r.json()
        except Exception:
            raise TuisongbaoError('got invalid response')

        if result['ack'] != '0':
            raise TuisongbaoError(result['error'].encode('utf-8'), result['ack'])

        return result


class TuisongbaoError(Exception):
    def __init__(self, msg, ack=None):
        self.msg = msg
        self.ack = ack

    def __str__(self):
        msg = self.msg
        if self.ack is not None:
            msg += (', ack: %s' % self.ack).encode('utf-8')

        return msg
