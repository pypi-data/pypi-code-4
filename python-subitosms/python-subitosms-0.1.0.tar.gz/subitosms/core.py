# -*- coding: iso-8859-1 -*-

TEMPLATE_JSON = {
    'url': 'https://www.subitosms.it/json.php',
    'auth': {'auth': {'username': None, 'password': None}},
    'error': {'message': 'Wrong username or password', 'code': 3},
    'credit': {
        'url': 'action=credit',
        'request': {'data': []},
        'response': {
            'data': {'Italy': '4021', 'Foreign': '91', 'ItalyLow': '90',
                     'AddressBooks': '12', 'Polls': '6', 'Credit': None}
        }
    },
    'status': {
        'url': 'action=status',
        'request': {'data': [{'id': 12293682}, {'id': 12279076}]},
        'response': {
            'data': [
                {'id': 12293682, 'messages': [
                    {'sender': 'Example1', 'dest': '+39335123456',
                     'text': 'First message', 'status': '1', 'code': 1803322}]},
                {'id': 12279076, 'messages': [
                    {'sender': 'Example2', 'dest': '+39335123456',
                     'text': 'Secondmessage', 'status': '1', 'code': 1741411},
                    {'sender': 'Example3', 'dest': '+39347123456',
                     'text': 'Third message', 'status': '1', 'code': 1741412}]}]
        }
    },
    'send_one_sms': {
        'url': 'action=send',
        'request': {'data': [
            {
                'sender': 'SubitoSMS',
                'dest': '+39335123456',
                'text': 'Hello message',
            }]},
        'response': {'data': {'id': '12293682'}}
    },
    'send_two_sms': {
        'url': 'action=send',
        'request': {'data': [
            {
                'sender': 'SubitoSMS',
                'dest': '+39335123456',
                'text': 'Hello message',
            },
            {
                'sender': 'SubitoSMS',
                'dest': '+393356359515',
                'text': 'Hello message',
            }]},
        'response': {'data': {'id': '12293682'}}
    }
}