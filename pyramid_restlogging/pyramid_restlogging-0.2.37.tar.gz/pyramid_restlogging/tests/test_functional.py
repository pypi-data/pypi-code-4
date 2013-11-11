# encoding: utf-8
import unittest
import json

import webtest


class TestLogView(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        from pyramid_restlogging import main
        self.app = webtest.TestApp(main(None))

    def test_basic(self):
        body = 'Error: no more spam'
        self.app.post('/clientlogs/spam/error', body, status=200)

    def test_wrong_encoding(self):
        body = u'Unknown user: Éric'.encode('latin-1')
        headers = {'Content-Type': 'text/plain; charset=utf-8'}
        self.app.post('/clientlogs/spam/error', body, headers, status=200)

    def test_invalid_loglevel(self):
        body = 'Error: too much ham'
        self.app.post('/clientlogs/spam/impossible', body, status=404)

    def test_logger_name_colon(self):
        self.app.post('/clientlogs/com.ludia::Test/error', status=200)


class TestBatchLogView(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        from pyramid_restlogging import main
        self.app = webtest.TestApp(main(None))

    def test_one_statement(self):
        data = json.dumps(
            {'logs': [{
                'log_level': 'debug',
                'logger_name': 'com.ludia::Test',
                'body': 'lol',
                },
            ]}
        )
        headers = {'Content-Type': 'application/json'}
        self.app.post('/clientlogs/batch', data, headers=headers, status=200)

    def test_multiple_statements(self):
        data = json.dumps(
            {'logs': [{
                'log_level': 'debug',
                'logger_name': 'com.ludia::Test',
                'body': 'lol',
                }, {
                'log_level': 'warn',
                'logger_name': 'com.ludia::Test',
                'body': 'haha',
                },
            ]}
        )
        headers = {'Content-Type': 'application/json'}
        self.app.post('/clientlogs/batch', data, headers=headers, status=200)

    def test_invalid_log_level(self):
        data = json.dumps(
            {'logs': [{
                'log_level': 'danger',
                'logger_name': 'com.ludia::Test',
                'body': 'lol',
                },
            ]}
        )
        headers = {'Content-Type': 'application/json'}
        self.app.post('/clientlogs/batch', data, headers=headers, status=400)

    def test_empty_logs_1(self):
        data = json.dumps(
            {'logs': [{
                },
            ]}
        )
        headers = {'Content-Type': 'application/json'}
        self.app.post('/clientlogs/batch', data, headers=headers, status=400)

    def test_empty_logs_2(self):
        data = json.dumps(
            {'statements': [{
                'log_level': 'danger',
                'logger_name': 'com.ludia::Test',
                'body': 'lol',
                },
            ]}
        )
        headers = {'Content-Type': 'application/json'}
        self.app.post('/clientlogs/batch', data, headers=headers, status=400)
