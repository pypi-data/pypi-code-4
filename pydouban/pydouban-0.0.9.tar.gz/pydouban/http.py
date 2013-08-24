#encoding:utf-8
"""
Copyright 2013 TY<tianyu0915@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import os
import logging
import socket
import shelve
from hashlib import md5
import requests
logger = logging.getLogger(__name__)


class HttpHanlder:

    def __init__(self,headers=None,session_key='new_session'):
        self.headers = headers
        self.session_key = md5(session_key).hexdigest()

    def _get_session(self):
        """ Get requests session form  a db file
        
        """
        config = { 
            'max_retries': 5,
            'pool_connections': 10, 
            'pool_maxsize': 10, 
        }

        try:
            new_session = requests.Session(prefetch=True, timeout=30, config=config,headers=self.headers)
        except:
            new_session = requests.Session()
        db = self._get_tmp_db()
        return db.get(self.session_key,new_session)

    def _http_request(self,method,url,data):
        self.br = self._get_session()
        try:
            if method.lower() == 'get':
                html  = self.br.get(url,params=data).content
            elif method.lower() == 'post':
                html = self.br.post(url,data=data,verify=True).content
        except (socket.timeout,requests.exceptions.Timeout):
            logger.exception('http timeout,method:{},url:{},params:{}'.format(method,url,data))
            return None
        else:
            logger.info('http request,method:{},url:{},params:{}'.format(method,url,data))
            return html

    def get(self,url,params=None):
        return self._http_request('get',url,params)

    def post(self,url,data):
        return self._http_request('post',url,data)

    def save_session(self):
        """ Save a new `requests.session` object into file db 
        
        """
        db = self._get_tmp_db()
        db[self.session_key] = self.br
        return db.close()

    def _get_tmp_db(self):
        """ Return a `shelve` object 
        
        """
        return shelve.open('/usr/local/var/pydouban_session')

    def clear_tmp_db(self):
        """ Remove db file 

        """
        try:
            os.remove('tmp.db')
        except:
            pass


