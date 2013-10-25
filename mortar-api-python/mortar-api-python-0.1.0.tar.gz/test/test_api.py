#
# Copyright 2013 Mortar Data Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import unittest

import mock
from requests.exceptions import HTTPError

from mortar.api.v2 import api


class TestAPI(unittest.TestCase):
    
    def setUp(self):
        self.email = 'unittest@x-y-z.com'
        self.api_key = 'YYYYYYYYYYYYYYYYYY'
        self.scheme = 'https'
        self.host = 'localhost'
    
    def test_url(self):
        test_api = api.API(self.email, self.api_key, self.scheme, self.host)
        self.assertEquals('https://localhost/v2/jobs', test_api.url('jobs'))
    
    @mock.patch('mortar.api.v2.api.requests')
    def test_post(self, requests_mock):
        test_api = api.API(self.email, self.api_key, self.scheme, self.host)
        path = 'foo/bar'
        payload = {'param0': 'bar'}
        
        url = 'https://localhost/v2/%s' % path
        json_payload = '{"param0": "bar"}'
        
        response_mock = mock.Mock()
        response_mock.raise_for_status.return_value = None
        
        return_json = {'success': True}
        response_mock.json.return_value = return_json
        requests_mock.post.return_value = response_mock
        
        response_json = test_api.post(path, payload)
        self.assertEquals(return_json, response_json)

        requests_mock.post.assert_called_with(url, data=json_payload, auth=test_api.auth, headers=api.API.HEADERS)
    
    @mock.patch('mortar.api.v2.api.requests')
    def test_post_error(self, requests_mock):
        test_api = api.API(self.email, self.api_key, self.scheme, self.host)
        path = 'foo/bar'
        payload = {'param0': 'bar'}

        url = 'https://localhost/v2/%s' % path
        json_payload = '{"param0": "bar"}'

        response_mock = mock.Mock()
        response_mock.raise_for_status.side_effect = HTTPError('400 Client Error: Bad Request')
        requests_mock.post.return_value = response_mock
        
        self.assertRaises(HTTPError, test_api.post, path, payload)

    @mock.patch('mortar.api.v2.api.requests')
    def test_get(self, requests_mock):
        test_api = api.API(self.email, self.api_key, self.scheme, self.host)
        path = 'foo/bar'
        params = {'param0': 'dolphin', 'param1': 'orca'}
    
        url = 'https://localhost/v2/%s' % path
        json_payload = '{"param0": "bar"}'
    
        response_mock = mock.Mock()
        response_mock.raise_for_status.return_value = None
        return_json = {'success': True}
        response_mock.json.return_value = return_json
        requests_mock.get.return_value = response_mock
    
        response_json = test_api.get(path, params=params)
        self.assertEquals(return_json, response_json)
        requests_mock.get.assert_called_with(url, params=params, auth=test_api.auth, headers=api.API.HEADERS)

    @mock.patch('mortar.api.v2.api.requests')
    def test_get_error(self, requests_mock):
        test_api = api.API(self.email, self.api_key, self.scheme, self.host)
        path = 'foo/bar'
        params = {'param0': 'dolphin', 'param1': 'orca'}

        url = 'https://localhost/v2/%s' % path
        json_payload = '{"param0": "bar"}'

        response_mock = mock.Mock()
        response_mock.raise_for_status.side_effect = HTTPError('400 Client Error: Bad Request')
        requests_mock.get.return_value = response_mock
        
        self.assertRaises(HTTPError, test_api.get, path, params)

    @mock.patch('mortar.api.v2.api.requests')
    def test_put(self, requests_mock):
        test_api = api.API(self.email, self.api_key, self.scheme, self.host)
        path = 'foo/bar'
        payload = {'param0': 'bar'}

        url = 'https://localhost/v2/%s' % path
        json_payload = '{"param0": "bar"}'

        response_mock = mock.Mock()
        response_mock.raise_for_status.return_value = None

        return_json = {'success': True}
        response_mock.json.return_value = return_json
        requests_mock.put.return_value = response_mock

        response_json = test_api.put(path, payload)
        self.assertEquals(return_json, response_json)

        requests_mock.put.assert_called_with(url, data=json_payload, auth=test_api.auth, headers=api.API.HEADERS)

    @mock.patch('mortar.api.v2.api.requests')
    def test_put_error(self, requests_mock):
        test_api = api.API(self.email, self.api_key, self.scheme, self.host)
        path = 'foo/bar'
        payload = {'param0': 'bar'}

        url = 'https://localhost/v2/%s' % path
        json_payload = '{"param0": "bar"}'

        response_mock = mock.Mock()
        response_mock.raise_for_status.side_effect = HTTPError('400 Client Error: Bad Request')
        requests_mock.put.return_value = response_mock

        self.assertRaises(HTTPError, test_api.put, path, payload)

    @mock.patch('mortar.api.v2.api.requests')
    def test_delete(self, requests_mock):
        test_api = api.API(self.email, self.api_key, self.scheme, self.host)
        path = 'foo/bar'

        url = 'https://localhost/v2/%s' % path

        response_mock = mock.Mock()
        response_mock.raise_for_status.return_value = None
        return_json = {'success': True}
        response_mock.json.return_value = return_json
        requests_mock.delete.return_value = response_mock

        test_api.delete(path)
        requests_mock.delete.assert_called_with(url, auth=test_api.auth, headers=api.API.HEADERS)

    @mock.patch('mortar.api.v2.api.requests')
    def test_delete_error(self, requests_mock):
        test_api = api.API(self.email, self.api_key, self.scheme, self.host)
        path = 'foo/bar'
        url = 'https://localhost/v2/%s' % path
        response_mock = mock.Mock()
        response_mock.raise_for_status.side_effect = HTTPError('400 Client Error: Bad Request')
        requests_mock.delete.return_value = response_mock

        self.assertRaises(HTTPError, test_api.delete, path)
