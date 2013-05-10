# -*- coding: utf-8 -*-

import copy
import json
from unittest import TestCase, main

try:
    from unittest.mock import MagicMock, patch, call
except ImportError:
    from mock import MagicMock, patch, call

from ..core import TEMPLATE_JSON
from ..gateways import JsonGatewaySubitoSms, PhpGatewaySubitoSms


class TestGateway(TestCase):

    def setUp(self):
        self.username = '_username_'
        self.password = '_password_'
        self.sender = 'fake' * 5
        self.dest = '+393330022111'
        self.dests = [self.dest[:-1] + str(ix) for ix in range(1, 6)]
        self.text = 'Messaggio di test.'
        self.sms_data = [{'sender': self.sender, 'dest': self.dest,
                          'text': self.text}]


class TestLogicJsonGateway(TestGateway):
    def setUp(self):
        super(TestLogicJsonGateway, self).setUp()
        self.gateway = JsonGatewaySubitoSms(username=self.username,
                                            password=self.password,
                                            test=False)
        self.template_json = copy.deepcopy(TEMPLATE_JSON)
        self.template_json['auth']['auth']['username'] = self.username
        self.template_json['auth']['auth']['password'] = self.password

    def tearDown(self):
        del self.template_json

    def _get_prepared_data(self, action):
        data = copy.deepcopy(self.template_json['auth'])
        data.update(self.template_json[action]['request'])
        return json.dumps(data)

    def _get_url(self, action, **kwargs):
        return '{}?action={}{}'.format(
            self.template_json['url'],
            action,
            ''.join(['&{}={}'.format(k, kwargs[k]) for k in kwargs]))

    def test_init_method(self):
        """
        Test init method
        """
        gateway = JsonGatewaySubitoSms(username=self.username,
                                       password=self.password,
                                       test=True)
        self.assertEqual(gateway._username, self.username)
        self.assertEqual(gateway._password, self.password)
        self.assertTrue(gateway.test)
        self.assertEqual(gateway._url, self.template_json['url'])

    def test_get_auth_data_mehod(self):
        data = self.gateway.get_auth_data()
        self.assertDictEqual(data, self.template_json['auth'])

    @patch('subitosms.gateways.JsonGatewaySubitoSms.get_auth_data')
    def test_prepare_data_methid_without_data_paramenter(self, mock_auth):
        mock_auth.return_value = self.template_json['auth']
        result = json.loads(self.gateway.prepare_data())
        mock_auth.assert_called_once_with()
        self.assertTrue('data' in result)
        self.assertEqual(result['data'], [])

    @patch('subitosms.gateways.JsonGatewaySubitoSms.get_auth_data')
    def test_prepare_data_methid_with_data_paramenter(self, mock_auth):
        data = [{'key': 'value'}]
        mock_auth.return_value = self.template_json['auth']
        result = json.loads(self.gateway.prepare_data(data=data))
        mock_auth.assert_called_once_with()
        self.assertTrue('data' in result)
        self.assertEqual(result['data'], data)

    @patch('subitosms.gateways.urlopen')
    @patch('subitosms.gateways.Request')
    @patch('subitosms.gateways.JsonGatewaySubitoSms.prepare_data')
    def test_make_request_method(self, mock_prepare_data, mock_request,
                                 mock_urlopen):
        action = 'credit'
        data = None
        mock_prepare_data.return_value = self._get_prepared_data(action)
        request = mock_request.return_value
        config = {'return_value.read.return_value': json.dumps(
            self.template_json[action]['response'])}
        mock_urlopen.configure_mock(**config)
        result = self.gateway.make_request(action=action)
        mock_prepare_data.assert_called_once_with(data=data)
        mock_request.assert_called_oncewith(self._get_url(action),
                                            mock_prepare_data.return_value)
        self.assertEqual(mock_urlopen.mock_calls,
                         call(request).read().call_list())
        self.assertIsInstance(result, dict)
        self.assertDictEqual(result, self.template_json[action]['response'])

    @patch('subitosms.gateways.JsonGatewaySubitoSms.make_request')
    def test_check_credit_method(self, mock_make_request):
        self.gateway.check_credit()
        mock_make_request.assert_called_once_with(action='credit')

    @patch('subitosms.gateways.JsonGatewaySubitoSms.check_credit')
    def test_remaining_sms_credit_method(self, mock_check_credit):
        mock_check_credit.return_value = (
            self.template_json['credit']['response'])
        result = self.gateway.remaining_sms_credit()
        mock_check_credit.assert_called_once_with()
        self.assertEqual(
            result,
            int(self.template_json['credit']['response']['data']['Italy']))

    @patch('subitosms.gateways.JsonGatewaySubitoSms.make_request')
    def send_sms_method(self, mock_make_request):
        sms_data = self.template_json['send_one_sms']['request']['data']
        mock_make_request.return_value = (
            self.template_json['send_one_sms']['response'])
        result = self.gateway.send_sms()
        mock_make_request.assert_called_once_with(action='send', data=sms_data)








# class TestJsonGatewaySubitoSms(TestGateway):
#
#     def setUp(self):
#         super(TestJsonGatewaySubitoSms, self).setUp()
#         self.gateway = JsonGatewaySubitoSms(username=self.real_username,
#                                             password=self.real_password,
#                                             test=True)
#
#     def test_prepare_data_without_data(self):
#         print(self.gateway.prepare_data())
#         print(self.gateway.prepare_data(data=self.sms_data))
#
#     def test_check_credit(self):
#         result = self.gateway.check_credit()
#         self.assertIs(type(result), dict)
#         self.assertIn('data', result.keys())
#         self.assertIn('Italy', result['data'].keys())
#
#     def test_remaing_sms_credit(self):
#         result = self.gateway.remaing_sms_credit()
#         self.assertIs(type(result), int)

#     def test_send_sms(self):
#         pre_n_sms = self.gateway.remaing_sms_credit()
#         result = self.gateway.send_sms(self.dest, self.text, sender=self.sender)
#         self.assertIn('data', result.keys())
#         self.assertIn('id', result['data'].keys())
#         self.assertIs(type(result['data']['id']), int)
#         sms_id = result['data']['id']
#         status = self.gateway.check_status(sms_id)
#         self.assertIs(type(status), list)
#         self.assertEqual(len(status), 1)
#         self.assertIn('id', status[0].keys())
#         self.assertEqual(status[0]['id'], sms_id)
#         self.assertIn('messages', status[0].keys())
#         self.assertEqual(len(status[0]['messages']), 1)
#         self.assertIn(status[0]['messages'][0]['status'], [0, '0', '16'])
#         self.assertEqual(pre_n_sms, self.gateway.remaing_sms_credit())
#
#     def test_send_bulk_sms(self):
#         pre_n_sms = self.gateway.remaing_sms_credit()
#         result = self.gateway.send_bulk_sms(self.dests, self.text,
#                                             sender=self.sender)
#         self.assertIn('data', result.keys())
#         self.assertIn('id', result['data'].keys())
#         self.assertIs(type(result['data']['id']), int)
#         bulk_id = result['data']['id']
#         status = self.gateway.check_status(bulk_id)
#         self.assertIs(type(status), list)
#         self.assertEqual(len(status), 1)
#         self.assertIn('id', status[0].keys())
#         self.assertEqual(status[0]['id'], bulk_id)
#         self.assertIn('messages', status[0].keys())
#         self.assertEqual(len(status[0]['messages']), len(self.dests))
#         for message in status[0]['messages']:
#             self.assertIn(message['status'], [0, '0', '16'])
#         self.assertEqual(pre_n_sms, self.gateway.remaing_sms_credit())
#
#
# class TestPhpGatewaySubitoSms(TestGatewaySubitoSms):
#
#     def setUp(self):
#         super(TestPhpGatewaySubitoSms, self).setUp()
#         self.sms_data = {'sender': self.sender, 'dest': self.dest,
#                          'text': self.text}
#         self.gateway = PhpGatewaySubitoSms(username=self.real_username,
#                                            password=self.real_password,
#                                            test=True)
#
#     # def test_prepare_data_without_data(self):
#     #     print self.gateway.prepare_data()
#     #     print self.gateway.prepare_data(**self.sms_data)
#
#     def test_check_credit(self):
#         result = self.gateway.check_credit()
#         self.assertIs(type(result), str)
#         self.assertEqual(result.find('credito'), 0)
#
#     def test_remaing_sms_credit(self):
#         result = self.gateway.remaing_sms_credit()
#         self.assertIs(type(result), int)
#
#     def test_send_sms(self):
#         pre_n_sms = self.gateway.remaing_sms_credit()
#         result = self.gateway.send_sms(self.dest, self.text, sender=self.sender)
#         self.assertIs(type(result), dict)
#         self.assertIn('id', result.keys())
#         self.assertIs(type(result['id']), str)
#         self.assertEqual(pre_n_sms, self.gateway.remaing_sms_credit())
#         sms_id = result['id']
#         status = self.gateway.check_status(sms_id)
#         self.assertIs(type(status), list)
#         self.assertEqual(len(status), 1)
#         self.assertListEqual(['dest', 'stato', 'desc'], status[0].keys())
#         self.assertEqual(status[0]['dest'], self.dest)
#         self.assertEqual(status[0]['stato'], '-2')
#
#     def test_send_bulk_sms(self):
#         pre_n_sms = self.gateway.remaing_sms_credit()
#         result = self.gateway.send_sms(self.dests, self.text,
#                                        sender=self.sender)
#         self.assertIs(type(result), dict)
#         self.assertIn('id', result.keys())
#         self.assertIs(type(result['id']), str)
#         self.assertEqual(pre_n_sms, self.gateway.remaing_sms_credit())
#         bulk_id = result['id']
#         status = self.gateway.check_status(bulk_id)
#         self.assertIs(type(status), list)
#         self.assertEqual(len(status), len(self.dests))
#         for s in status:
#             self.assertIn(s['dest'], self.dests)
#             self.assertEqual(s['stato'], '-2')
#         self.assertEqual(pre_n_sms, self.gateway.remaing_sms_credit())


if __name__ == '__main__':
    main()

