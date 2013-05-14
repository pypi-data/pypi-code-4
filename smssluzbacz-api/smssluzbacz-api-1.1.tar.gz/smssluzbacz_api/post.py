import logging
from hashlib import md5
from xml.dom.minidom import parseString

import requests

from smssluzbacz_api import TelephoneNumberError, MessageError, ActionError, LoginError, CreditError, \
    GateError, TRUNCATE_LIMIT, USER_AGENT


log = logging.getLogger(__name__)


class SmsGateApi(object):
    """Implements 'POST' version of sms.sluzba.cz HTTP API.

    Implements simple XML response protocol and uses advanced tokenized
    authentication.

    """

    ACTION_SEND = 'send'
    URL = 'http://smsgateapi.sluzba.cz/apipost20/sms'
    URL_SSL = 'https://smsgateapi.sluzba.cz/apipost20/sms'

    def __init__(self, login, password, timeout=2, use_ssl=True):
        """Initializes SmsGateApi class.

        :param login: sms.sluzba.cz login
        :type login: string
        :param password: password to sms.sluzba.cz
        :type password: string
        :param timeout: http connection timeout in seconds
        :type timeout: int
        :param use_ssl: whether to use ssl via http or not
        :rtype use_ssl: bool
        :returns: SmsGateApi instance
        :rtype: smssluzbacz_api.post.SmsGateApi

        """
        self.login = login
        self.password = password
        self.timeout = timeout
        self.use_ssl = use_ssl

    def send(self, tel_number, message):
        """Sends SMS via sms.sluzba.cz.

        :param tel_number: telephone number of SMS receiver
        :type tel_number: string
        :param message: text body of SMS
        :type message: string
        :returns: True is SMS was successfully sent
        :rtype: bool
        :raises: ValueError, urllib2.URLError, urllib2.HTTPError, GateError
        :raises: TelephoneNumberError, MessageError, ActionError, LoginError
        :raises: CreditError

        """
        if message is not None and len(message) > TRUNCATE_LIMIT:
            log.warn('Message text exceeds %d characters and will be automatically truncated', TRUNCATE_LIMIT)
        params = (
            ('msg', message),
            ('msisdn', tel_number),
            ('act', SmsGateApi.ACTION_SEND),
            ('login', self.login),
            ('auth', self.__get_auth_key(message))
        )
        log.debug('Post params built: %s', params)
        log.info('Sending SMS to number: %s, message text: %s', tel_number, message)
        response = requests.post(SmsGateApi.URL_SSL if self.use_ssl else SmsGateApi.URL, data=dict(params),
                                 headers={'User-Agent': USER_AGENT, 'Accept': 'text/plain'}, timeout=self.timeout)
        if response.status_code != 200:
            raise GateError
        dom = parseString(response.text)
        code = dom.getElementsByTagName('id')[0].childNodes[0].data
        if code == TelephoneNumberError.code:
            raise TelephoneNumberError
        elif code == MessageError.code:
            raise MessageError
        elif code == ActionError.code:
            raise ActionError
        elif code == LoginError.code:
            raise LoginError
        elif code == CreditError.code:
            raise CreditError
        elif code == GateError.code:
            raise GateError
        elif code == '200':
            log.info('SMS message successfully sent to %s.', tel_number)
            return True

    def __get_auth_key(self, message):
        return md5(md5(self.password).hexdigest() + self.login + SmsGateApi.ACTION_SEND + message[:31]).hexdigest()