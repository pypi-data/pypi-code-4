#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org
          Sebastián Ortiz V. neoecos@gmail.com

SIIM Server is the web server of SIIM's Framework
Copyright (C) 2013 Infometrika Ltda

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
# -*- coding: utf-8 -*-
import os
from cid import caliope_server
import unittest
import json
import uuid
import hashlib


class SIIM2ServerTestCase(unittest.TestCase):

    def setUp(self):
        """Before each test, set up a blank enviroment"""
        caliope_server.app.config['TESTING'] = True
        caliope_server.init_flask_app()
        caliope_server.configure_server_and_app("conf/caliope_server.json")
        caliope_server.configure_logger("conf/logger.json")
        caliope_server.register_modules()
        self.app = caliope_server.app.test_client()

    def tearDown(self):
        """Get rid of the database again after each test."""
        pass

    def login(self, username, password, callback_id):
        data = dict(cmd="authentication",
                    login=username,
                    password=password,
                    callback_id=callback_id
                    )
        response = self.app.post('/api/rest', data=json.dumps(data),
                                 content_type='application/json')
        return response

    # testing functions
    def test_login(self):
        """Make sure login works"""
        callback_id = str(uuid.uuid4()).decode('utf-8')
        rv = self.login('user',
                        hashlib.sha256('password').hexdigest(),
                        callback_id)
        response = json.loads(rv.data)
        assert response['result'] == 'ok'
        assert response['callback_id'] == callback_id
        assert 'uuid' in response['data']


if __name__ == '__main__':
    unittest.main()
