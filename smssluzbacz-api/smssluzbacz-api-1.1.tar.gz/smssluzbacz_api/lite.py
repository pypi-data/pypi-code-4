import re
import logging
import urllib

import requests

from smssluzbacz_api import TelephoneNumberError, MessageError, ActionError, LoginError, CreditError,\
    GateError, TRUNCATE_LIMIT, USER_AGENT


log = logging.getLogger(__name__)


__all__ = ['SmsGateApi']


class SmsGateApi(object):
    """Implements 'Lite' version of sms.sluzba.cz HTTP API.

    The only possibility of lite version is to send POST/GET request to send SMS
    with no advanced options and operations.

    """
    URL = 'http://smsgateapi.sluzba.cz/apilite20/sms'
    URL_SSL = 'https://smsgateapi.sluzba.cz/apilite20/sms'

    def __init__(self, login, password, timeout=2, use_ssl=True):
        """Initializes SmsGateApi class.

        :param login: sms.sluzba.cz login
        :type login: string
        :param password: password to sms.sluzba.cz
        :type password: string
        :param timeout: http connection timeout in seconds
        :type timeout: int
        :param use_ssl: whether to use ssl via http or not
        :type use_ssl: bool
        :returns: SmsGateApi instance
        :rtype: smssluzbacz_api.lite.SmsGateApi

        """
        self.login = login
        self.password = password
        self.timeout = timeout
        self.use_ssl = use_ssl

    def send(self, tel_number, message, use_post=True):
        """Sends SMS via sms.sluzba.cz.

        :param tel_number: telephone number of SMS receiver
        :type tel_number: string
        :param message: text body of SMS
        :type message: string
        :param use_post: whether to use GET or POST http method
        :type use_post: bool
        :returns: True is SMS was successfully sent
        :rtype: bool
        :raises: ValueError, urllib2.URLError, urllib2.HTTPError, GateError
        :raises: TelephoneNumberError, MessageError, ActionError, LoginError
        :raises: CreditError

        """
        if message is not None and len(message) > TRUNCATE_LIMIT:
            log.warn('Message text exceeds %d characters and will be automatically truncated', TRUNCATE_LIMIT)
        params = (
            ('login', self.login),
            ('password', self.password),
            ('number', tel_number),
            ('text', message)
        )
        log.debug('Params built: %s', params)
        log.info('Sending SMS to number: %s, message text: %s', tel_number, message)
        if use_post:
            response = requests.post(SmsGateApi.URL_SSL if self.use_ssl else SmsGateApi.URL, data=dict(params),
                                     headers={'User-Agent': USER_AGENT, 'Accept': 'text/plain'},
                                     timeout=self.timeout)
        else:
            encoded_params = urllib.urlencode(params)
            if self.use_ssl:
                encoded_url = '?'.join([SmsGateApi.URL_SSL, encoded_params])
            else:
                encoded_url = '?'.join([SmsGateApi.URL, encoded_params])
            response = requests.get(encoded_url, headers={'User-Agent': USER_AGENT}, timeout=self.timeout)
        if response.status_code != 200:
            raise GateError
        if re.match(r'^{0}'.format(TelephoneNumberError.code), response.text) is not None:
            raise TelephoneNumberError
        elif re.match(r'^{0}'.format(MessageError.code), response.text) is not None:
            raise MessageError
        elif response.text[:3] == ActionError.code:
            raise ActionError
        elif response.text[:3] == LoginError.code:
            raise LoginError
        elif response.text[:3] == CreditError.code:
            raise CreditError
        elif response.text[:3] == GateError.code:
            raise GateError
        elif response.text[:3] == '200':
            log.info('SMS message successfully sent to %s.', tel_number)
            return True