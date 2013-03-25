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


class LocationsApi(object):

    def __init__(self, apiClient):
      self.apiClient = apiClient

    
    def getAllLocations(self, api_key, **kwargs):
        """Get all of your locations

        Args:
            api_key, str: Subtledata API Key (required)
            use_cache, bool: Utilize Cached Data (optional)
            
        Returns: list[Location]
        """

        allParams = ['api_key', 'use_cache']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method getAllLocations" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/locations'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('use_cache' in params):
            queryParams['use_cache'] = self.apiClient.toPathValue(params['use_cache'])
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'list[Location]')
        return responseObject
        
        
    def createLocation(self, api_key, body, **kwargs):
        """Create a ticket

        Args:
            api_key, str: Subtledata API Key (required)
            body, NewTicket: New Ticket Object (required)
            
        Returns: TicketStatus
        """

        allParams = ['api_key', 'body']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method createLocation" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/locations'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'POST'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'TicketStatus')
        return responseObject
        
        
    def getLocationsNear(self, api_key, latitude, longitude, radius, **kwargs):
        """Get locations near a GPS coordinate

        Args:
            api_key, str: Subtledata API Key (required)
            use_cache, bool: Utilize Cached Data (optional)
            latitude, float: Latitude floating point value of search coordinate (required)
            longitude, float: Longitude floating point value of search coordinate (required)
            radius, float: Distance (in miles) to search near coordinate (required)
            
        Returns: list[Location]
        """

        allParams = ['api_key', 'use_cache', 'latitude', 'longitude', 'radius']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method getLocationsNear" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/locations/filter/near'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('use_cache' in params):
            queryParams['use_cache'] = self.apiClient.toPathValue(params['use_cache'])
        if ('latitude' in params):
            queryParams['latitude'] = self.apiClient.toPathValue(params['latitude'])
        if ('longitude' in params):
            queryParams['longitude'] = self.apiClient.toPathValue(params['longitude'])
        if ('radius' in params):
            queryParams['radius'] = self.apiClient.toPathValue(params['radius'])
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'list[Location]')
        return responseObject
        
        
    def getLocation(self, location_id, api_key, **kwargs):
        """Get a location by ID

        Args:
            location_id, int: Subtledata Location ID (required)
            api_key, str: Subtledata API Key (required)
            use_cache, bool: Utilize Cached Data (optional)
            
        Returns: Location
        """

        allParams = ['location_id', 'api_key', 'use_cache']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method getLocation" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/locations/{location_id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('use_cache' in params):
            queryParams['use_cache'] = self.apiClient.toPathValue(params['use_cache'])
        if ('location_id' in params):
            replacement = str(self.apiClient.toPathValue(params['location_id']))
            resourcePath = resourcePath.replace('{' + 'location_id' + '}',
                                                replacement)
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'Location')
        return responseObject
        
        
    def updateLocation(self, location_id, api_key, **kwargs):
        """Update a location

        Args:
            location_id, int: Subtledata Location ID (required)
            api_key, str: Subtledata API Key (required)
            
        Returns: Status
        """

        allParams = ['location_id', 'api_key']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method updateLocation" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/locations/{location_id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'PUT'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('location_id' in params):
            replacement = str(self.apiClient.toPathValue(params['location_id']))
            resourcePath = resourcePath.replace('{' + 'location_id' + '}',
                                                replacement)
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'Status')
        return responseObject
        
        
    def deleteLocation(self, location_id, api_key, **kwargs):
        """Delete a location

        Args:
            location_id, int: Subtledata Location ID (required)
            api_key, str: Subtledata API Key (required)
            
        Returns: Status
        """

        allParams = ['location_id', 'api_key']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method deleteLocation" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/locations/{location_id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'DELETE'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('location_id' in params):
            replacement = str(self.apiClient.toPathValue(params['location_id']))
            resourcePath = resourcePath.replace('{' + 'location_id' + '}',
                                                replacement)
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'Status')
        return responseObject
        
        
    def getLocationMenu(self, location_id, api_key, **kwargs):
        """Get a location's Menu

        Args:
            location_id, int: Subtledata Location ID (required)
            api_key, str: Subtledata API Key (required)
            use_cache, bool: Utilize Cached Data (optional)
            
        Returns: list[Category]
        """

        allParams = ['location_id', 'api_key', 'use_cache']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method getLocationMenu" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/locations/{location_id}/menu'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('use_cache' in params):
            queryParams['use_cache'] = self.apiClient.toPathValue(params['use_cache'])
        if ('location_id' in params):
            replacement = str(self.apiClient.toPathValue(params['location_id']))
            resourcePath = resourcePath.replace('{' + 'location_id' + '}',
                                                replacement)
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'list[Category]')
        return responseObject
        
        
    def getTableList(self, location_id, api_key, **kwargs):
        """Get a list of tables by location ID

        Args:
            location_id, int: Subtledata Location ID (required)
            api_key, str: Subtledata API Key (required)
            
        Returns: TableList
        """

        allParams = ['location_id', 'api_key']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method getTableList" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/locations/{location_id}/tables'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('location_id' in params):
            replacement = str(self.apiClient.toPathValue(params['location_id']))
            resourcePath = resourcePath.replace('{' + 'location_id' + '}',
                                                replacement)
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'TableList')
        return responseObject
        
        
    def getTickets(self, location_id, api_key, **kwargs):
        """Get a list of tickets by location ID

        Args:
            location_id, int: Subtledata Location ID (required)
            api_key, str: Subtledata API Key (required)
            
        Returns: list[Ticket]
        """

        allParams = ['location_id', 'api_key']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method getTickets" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/locations/{location_id}/tickets'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('location_id' in params):
            replacement = str(self.apiClient.toPathValue(params['location_id']))
            resourcePath = resourcePath.replace('{' + 'location_id' + '}',
                                                replacement)
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'list[Ticket]')
        return responseObject
        
        
    def createTicket(self, location_id, api_key, body, **kwargs):
        """Create a ticket

        Args:
            location_id, int: Subtledata Location ID (required)
            api_key, str: Subtledata API Key (required)
            ticket_type, str: Order Type (optional)
            body, NewTicket: New Ticket Object (required)
            
        Returns: TicketStatus
        """

        allParams = ['location_id', 'api_key', 'ticket_type', 'body']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method createTicket" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/locations/{location_id}/tickets'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'POST'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('ticket_type' in params):
            queryParams['ticket_type'] = self.apiClient.toPathValue(params['ticket_type'])
        if ('location_id' in params):
            replacement = str(self.apiClient.toPathValue(params['location_id']))
            resourcePath = resourcePath.replace('{' + 'location_id' + '}',
                                                replacement)
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'TicketStatus')
        return responseObject
        
        
    def getTable(self, location_id, table_id, api_key, **kwargs):
        """Get a table by location ID and unique ID

        Args:
            location_id, int: Subtledata Location ID (required)
            table_id, int: Subtledata Location ID (required)
            api_key, str: Subtledata API Key (required)
            
        Returns: TableDetails
        """

        allParams = ['location_id', 'table_id', 'api_key']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method getTable" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/locations/{location_id}/tables/{table_id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('location_id' in params):
            replacement = str(self.apiClient.toPathValue(params['location_id']))
            resourcePath = resourcePath.replace('{' + 'location_id' + '}',
                                                replacement)
        if ('table_id' in params):
            replacement = str(self.apiClient.toPathValue(params['table_id']))
            resourcePath = resourcePath.replace('{' + 'table_id' + '}',
                                                replacement)
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'TableDetails')
        return responseObject
        
        
    def getTicket(self, location_id, ticket_id, api_key, **kwargs):
        """Get a ticket by ID

        Args:
            location_id, int: SubtleData Location ID (required)
            ticket_id, int: SubtleData Location ID (required)
            api_key, str: Subtledata API Key (required)
            user_id, int:  (optional)
            
        Returns: Ticket
        """

        allParams = ['location_id', 'ticket_id', 'api_key', 'user_id']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method getTicket" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/locations/{location_id}/tickets/{ticket_id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('user_id' in params):
            queryParams['user_id'] = self.apiClient.toPathValue(params['user_id'])
        if ('location_id' in params):
            replacement = str(self.apiClient.toPathValue(params['location_id']))
            resourcePath = resourcePath.replace('{' + 'location_id' + '}',
                                                replacement)
        if ('ticket_id' in params):
            replacement = str(self.apiClient.toPathValue(params['ticket_id']))
            resourcePath = resourcePath.replace('{' + 'ticket_id' + '}',
                                                replacement)
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'Ticket')
        return responseObject
        
        
    def voidTicket(self, location_id, ticket_id, api_key, **kwargs):
        """Void a ticket

        Args:
            location_id, int: SubtleData Location ID (required)
            ticket_id, int: SubtleData Location ID (required)
            api_key, str: Subtledata API Key (required)
            user_id, int:  (optional)
            
        Returns: Status
        """

        allParams = ['location_id', 'ticket_id', 'api_key', 'user_id']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method voidTicket" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/locations/{location_id}/tickets/{ticket_id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'DELETE'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('user_id' in params):
            queryParams['user_id'] = self.apiClient.toPathValue(params['user_id'])
        if ('location_id' in params):
            replacement = str(self.apiClient.toPathValue(params['location_id']))
            resourcePath = resourcePath.replace('{' + 'location_id' + '}',
                                                replacement)
        if ('ticket_id' in params):
            replacement = str(self.apiClient.toPathValue(params['ticket_id']))
            resourcePath = resourcePath.replace('{' + 'ticket_id' + '}',
                                                replacement)
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'Status')
        return responseObject
        
        
    def submitOrder(self, location_id, ticket_id, user_id, api_key, body, **kwargs):
        """Order the currently staged items

        Args:
            location_id, int: SubtleData Location ID (required)
            ticket_id, int: SubtleData Location ID (required)
            user_id, int: SubtleData Location ID (required)
            api_key, str: Subtledata API Key (required)
            body, SendTicket: Send the ticket (required)
            
        Returns: OrderResults
        """

        allParams = ['location_id', 'ticket_id', 'user_id', 'api_key', 'body']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method submitOrder" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/locations/{location_id}/tickets/{ticket_id}/users/{user_id}/order'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'POST'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('location_id' in params):
            replacement = str(self.apiClient.toPathValue(params['location_id']))
            resourcePath = resourcePath.replace('{' + 'location_id' + '}',
                                                replacement)
        if ('ticket_id' in params):
            replacement = str(self.apiClient.toPathValue(params['ticket_id']))
            resourcePath = resourcePath.replace('{' + 'ticket_id' + '}',
                                                replacement)
        if ('user_id' in params):
            replacement = str(self.apiClient.toPathValue(params['user_id']))
            resourcePath = resourcePath.replace('{' + 'user_id' + '}',
                                                replacement)
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'OrderResults')
        return responseObject
        
        
    def addItemsToOrder(self, location_id, ticket_id, user_id, api_key, body, **kwargs):
        """Add items to currently staged order on a ticket

        Args:
            location_id, int: SubtleData Location ID (required)
            ticket_id, int: SubtleData Location ID (required)
            user_id, int: SubtleData Location ID (required)
            api_key, str: Subtledata API Key (required)
            body, ItemToAdd: The Item object to Add (required)
            
        Returns: Status
        """

        allParams = ['location_id', 'ticket_id', 'user_id', 'api_key', 'body']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method addItemsToOrder" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/locations/{location_id}/tickets/{ticket_id}/users/{user_id}/order'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'PUT'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('location_id' in params):
            replacement = str(self.apiClient.toPathValue(params['location_id']))
            resourcePath = resourcePath.replace('{' + 'location_id' + '}',
                                                replacement)
        if ('ticket_id' in params):
            replacement = str(self.apiClient.toPathValue(params['ticket_id']))
            resourcePath = resourcePath.replace('{' + 'ticket_id' + '}',
                                                replacement)
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
        
        
    def discountTicket(self, location_id, ticket_id, api_key, body, **kwargs):
        """Discount a ticket

        Args:
            location_id, int: SubtleData Location ID (required)
            ticket_id, int: SubtleData Location ID (required)
            api_key, str: Subtledata API Key (required)
            body, DiscountInfo: Details regarding the discount (required)
            
        Returns: Status
        """

        allParams = ['location_id', 'ticket_id', 'api_key', 'body']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method discountTicket" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/locations/{location_id}/tickets/{ticket_id}/discount'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'POST'

        queryParams = {}
        headerParams = {}

        if ('api_key' in params):
            queryParams['api_key'] = self.apiClient.toPathValue(params['api_key'])
        if ('location_id' in params):
            replacement = str(self.apiClient.toPathValue(params['location_id']))
            resourcePath = resourcePath.replace('{' + 'location_id' + '}',
                                                replacement)
        if ('ticket_id' in params):
            replacement = str(self.apiClient.toPathValue(params['ticket_id']))
            resourcePath = resourcePath.replace('{' + 'ticket_id' + '}',
                                                replacement)
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'Status')
        return responseObject
        
        
    


