import unittest
import mock

import requests

from json_reference import Reference, InvalidReferenceError


class MockResponse(object):
    def __init__(self, content, status_code=200):
        self.content = content
        self.status_code = status_code


class ReferenceTest(unittest.TestCase):
    @mock.patch("requests.get", return_value=MockResponse('{"test": "bli"}'))
    def test_get(self, get):
        reference = Reference('http://localhost/#/test')
        result = reference.get()
        self.assertEqual(result, 'bli')

    @mock.patch("requests.get", return_value=MockResponse('{"test": "bli"}'))
    def test_get_root(self, get):
        reference = Reference('http://localhost/#')
        result = reference.get()
        self.assertEqual(result, {'test': 'bli'})

    @mock.patch("requests.get", return_value=MockResponse('Not found', 404))
    def test_get_error(self, get):
        reference = Reference('http://localhost/#')

        self.assertRaises(
            InvalidReferenceError,
            reference.get
        )

    @mock.patch("requests.get", return_value=MockResponse('{)', 200))
    def test_get_invalid_json(self, get):
        reference = Reference('http://localhost/#')

        self.assertRaises(
            InvalidReferenceError,
            reference.get
        )

    def test_register(self):
        Reference.register('http://localhost/', {'test': 'bli'})

        reference = Reference('http://localhost/#')
        result = reference.get()

        self.assertEqual(result, {'test': 'bli'})
