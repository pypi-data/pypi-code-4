#!/usr/bin/env python
"""
WordAPI.py
Copyright 2012 Wordnik, Inc.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

NOTE: This class is auto generated by the swagger code generator program. Do not edit the class manually.
"""
import sys
import os

from models import *


class UsersApi(object):

    def __init__(self, apiClient):
      self.apiClient = apiClient

    
    def createUser(self, api_key, body, **kwargs):
        """Create a user

        Args:
            api_key, str: Subtledata API Key (required)
            debug, bool: Internal Use Only (optional)
            body, NewUser: New User Object (required)
            
        Returns: User
        """

        allParams = ['api_key', 'debug', 'body']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method createUser" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/users'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'POST'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('debug' in params):
            queryParams['debug'] = self.apiClient.toPathValue(params['debug'])
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'User')
        return responseObject
        
        
    def getUser(self, user_id, api_key, **kwargs):
        """Get a user by ID

        Args:
            user_id, int: Subtledata User ID (required)
            api_key, str: Subtledata API Key (required)
            debug, bool: Internal Use Only (optional)
            use_cache, bool: Utilize Cached Data (optional)
            
        Returns: User
        """

        allParams = ['user_id', 'api_key', 'debug', 'use_cache']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method getUser" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/users/{user_id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('debug' in params):
            queryParams['debug'] = self.apiClient.toPathValue(params['debug'])
        if ('use_cache' in params):
            queryParams['use_cache'] = self.apiClient.toPathValue(params['use_cache'])
        if ('user_id' in params):
            replacement = str(self.apiClient.toPathValue(params['user_id']))
            resourcePath = resourcePath.replace('{' + 'user_id' + '}',
                                                replacement)
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'User')
        return responseObject
        
        
    def updateUser(self, user_id, api_key, **kwargs):
        """Update a user

        Args:
            user_id, int: Subtledata User ID (required)
            api_key, str: Subtledata API Key (required)
            debug, bool: Internal Use Only (optional)
            
        Returns: User
        """

        allParams = ['user_id', 'api_key', 'debug']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method updateUser" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/users/{user_id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'PUT'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('debug' in params):
            queryParams['debug'] = self.apiClient.toPathValue(params['debug'])
        if ('user_id' in params):
            replacement = str(self.apiClient.toPathValue(params['user_id']))
            resourcePath = resourcePath.replace('{' + 'user_id' + '}',
                                                replacement)
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'User')
        return responseObject
        
        
    def deleteUser(self, user_id, api_key, **kwargs):
        """Delete a user

        Args:
            user_id, int: Subtledata User ID (required)
            api_key, str: Subtledata API Key (required)
            debug, bool: Internal Use Only (optional)
            
        Returns: Status
        """

        allParams = ['user_id', 'api_key', 'debug']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method deleteUser" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/users/{user_id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'DELETE'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('debug' in params):
            queryParams['debug'] = self.apiClient.toPathValue(params['debug'])
        if ('user_id' in params):
            replacement = str(self.apiClient.toPathValue(params['user_id']))
            resourcePath = resourcePath.replace('{' + 'user_id' + '}',
                                                replacement)
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'Status')
        return responseObject
        
        
    def searchUsersByName(self, user_name, api_key, **kwargs):
        """Search for a user by name

        Args:
            user_name, str: Subtledata User Name (required)
            api_key, str: Subtledata API Key (required)
            debug, bool: Internal Use Only (optional)
            use_cache, bool: Utilize Cached Data (optional)
            
        Returns: list[User]
        """

        allParams = ['user_name', 'api_key', 'debug', 'use_cache']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method searchUsersByName" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/users/search/name/{user_name}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('debug' in params):
            queryParams['debug'] = self.apiClient.toPathValue(params['debug'])
        if ('use_cache' in params):
            queryParams['use_cache'] = self.apiClient.toPathValue(params['use_cache'])
        if ('user_name' in params):
            replacement = str(self.apiClient.toPathValue(params['user_name']))
            resourcePath = resourcePath.replace('{' + 'user_name' + '}',
                                                replacement)
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'list[User]')
        return responseObject
        
        
    def getUsersCards(self, user_id, api_key, **kwargs):
        """Get a list of stored cards for a user

        Args:
            user_id, int: SubtleData User ID (required)
            api_key, str: Subtledata API Key (required)
            debug, bool: Internal Use Only (optional)
            
        Returns: list[Card]
        """

        allParams = ['user_id', 'api_key', 'debug']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method getUsersCards" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/users/{user_id}/cards'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('debug' in params):
            queryParams['debug'] = self.apiClient.toPathValue(params['debug'])
        if ('user_id' in params):
            replacement = str(self.apiClient.toPathValue(params['user_id']))
            resourcePath = resourcePath.replace('{' + 'user_id' + '}',
                                                replacement)
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'list[Card]')
        return responseObject
        
        
    def createCardForUser(self, user_id, api_key, body, **kwargs):
        """Create a card for a user

        Args:
            user_id, int: SubtleData User ID (required)
            api_key, str: Subtledata API Key (required)
            debug, bool: Internal Use Only (optional)
            body, NewCard: New Card Object (required)
            
        Returns: CardStatus
        """

        allParams = ['user_id', 'api_key', 'debug', 'body']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method createCardForUser" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/users/{user_id}/cards'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'POST'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('debug' in params):
            queryParams['debug'] = self.apiClient.toPathValue(params['debug'])
        if ('user_id' in params):
            replacement = str(self.apiClient.toPathValue(params['user_id']))
            resourcePath = resourcePath.replace('{' + 'user_id' + '}',
                                                replacement)
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'CardStatus')
        return responseObject
        
        
    


