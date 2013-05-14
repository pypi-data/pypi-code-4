import unittest

from mock import patch, MagicMock

import smssluzbacz_api.lite
from smssluzbacz_api import TelephoneNumberError, MessageError, ActionError, LoginError, CreditError,\
    GateError


class TestSmsGateApiLite(unittest.TestCase):

    def setUp(self):
        self.response_mock = MagicMock()
        self.response_mock.status_code = None
        self.response_mock.text = ''

    def test_non_200_response_code(self):
        with patch('smssluzbacz_api.lite.requests') as mock:
            mock.post.return_value = self.response_mock
            self.response_mock.status_code = 100
            with self.assertRaises(GateError):
                api = smssluzbacz_api.lite.SmsGateApi('login', 'pass')
                api.send('123456789', 'message')

    def test_telephone_number_error(self):
        with patch('smssluzbacz_api.lite.requests') as mock:
            mock.post.return_value = self.response_mock
            self.response_mock.status_code = 200
            self.response_mock.text = '{0} neplatne cislo prijemce 12345-6789'.format(TelephoneNumberError.code)
            with self.assertRaises(TelephoneNumberError):
                api = smssluzbacz_api.lite.SmsGateApi('login', 'pass')
                api.send('12345-6789', 'message')

    def test_message_error(self):
        with patch('smssluzbacz_api.lite.requests') as mock:
            mock.post.return_value = self.response_mock
            self.response_mock.status_code = 200
            self.response_mock.text = '{0} Chybi text zpravy'.format(MessageError.code)
            with self.assertRaises(MessageError):
                api = smssluzbacz_api.lite.SmsGateApi('login', 'pass')
                api.send('123456789', '')

    def test_action_error(self):
        with patch('smssluzbacz_api.lite.requests') as mock:
            mock.post.return_value = self.response_mock
            self.response_mock.status_code = 200
            self.response_mock.text = '{0} Neznama akce'.format(ActionError.code)
            with self.assertRaises(ActionError):
                api = smssluzbacz_api.lite.SmsGateApi('login', 'pass')
                api.send('123456789', 'message')

    def test_login_error(self):
        with patch('smssluzbacz_api.lite.requests') as mock:
            mock.post.return_value = self.response_mock
            self.response_mock.status_code = 200
            self.response_mock.text = '{0} Chybne prihlaseni'.format(LoginError.code)
            with self.assertRaises(LoginError):
                api = smssluzbacz_api.lite.SmsGateApi('login', 'pass')
                api.send('123456789', 'message')

    def test_credit_error(self):
        with patch('smssluzbacz_api.lite.requests') as mock:
            mock.post.return_value = self.response_mock
            self.response_mock.status_code = 200
            self.response_mock.text = '{0} Nedostatecny kredit'.format(CreditError.code)
            with self.assertRaises(CreditError):
                api = smssluzbacz_api.lite.SmsGateApi('login', 'pass')
                api.send('123456789', 'message')

    def test_gate_error(self):
        with patch('smssluzbacz_api.lite.requests') as mock:
            mock.post.return_value = self.response_mock
            self.response_mock.status_code = 200
            self.response_mock.text = '{0} Chyba brany'.format(GateError.code)
            with self.assertRaises(GateError):
                api = smssluzbacz_api.lite.SmsGateApi('login', 'pass')
                api.send('123456789', 'message')

    def test_no_error(self):
        with patch('smssluzbacz_api.lite.requests') as mock:
            mock.post.return_value = self.response_mock
            self.response_mock.status_code = 200
            self.response_mock.text = '200 Zprava byla uspesne odeslana'
            api = smssluzbacz_api.lite.SmsGateApi('login', 'pass')
            result = api.send('123456789', 'message')
            self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()