import hashlib
import requests
from lxml import etree
from pprint import pprint


class SMSBoxService(object):
    """smsbox.sk service configuration

        [requirement fields]
        api_key
        signature

    :param api_key: Unique key identifier, assigned by smsbox.sk.
    :param signature: Unique signature, assigned by smsbox.sk.
    :param debug: Debug mode. If True, messages won't be send.
    :param format: Format of result data.
    """
    URL_SEND_MESSAGE = 'https://smsbox.sk:50443/interface/http-post/SendMessage.ashx'

    def __init__(self, api_key, signature, debug=False, format='XML'):
        self.api_key = api_key
        self.signature = signature
        self.debug = debug
        self.format = format


    def _get_sms_control_code(self, phone_number, message_text):
        """Generate control code for given phone number and message.

        :param phone_number: The phone number of SMS receiver.
        :param message_text: Message to be send.
        """

        def substr(s, start, length=None):
            """Returns the portion of string specified by the start and length
            parameters.
            """
            if start >= len(s):
                return False
            if not length:
                return s[start:]
            elif length > 0:
                return s[start:start + length]
            else:
                return s[start:length]

        user_signature = self.signature
        data2hash = '%(sig1)s%(phone_number)s%(sig2)s%(message_text)s%(sig3)s' % {
            'sig1': substr(user_signature, 0, 5),
            'phone_number': str(phone_number),
            'sig2': substr(user_signature, 5, 5),
            'message_text': str(message_text),
            'sig3': substr(user_signature, 10, 6)
        }
        return hashlib.sha256(data2hash).hexdigest()


    def send_sms(self, phone_number, message_text):
        payload = {
            'APIkey': self.api_key,
            'PhoneNumber': phone_number,
            'MessageText': message_text,
            'ControlCode': self._get_sms_control_code(phone_number, message_text),
            'TestMode': self.debug,
            'Format': self.format
        }
        post_result = requests.post(self.URL_SEND_MESSAGE, payload, allow_redirects=True)
        root = etree.fromstring(unicode(post_result.text).encode('utf-8'))
        #print etree.tostring(root)

        result = {}
        for key in root:
            result[key.tag] = root.find(key.tag).text

        #import xmltodict, json
        #o = xmltodict.parse(etree.tostring(root))
        #print json.dumps(o)

        return result
