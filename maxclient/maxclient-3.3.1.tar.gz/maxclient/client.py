import requests
import json
import urllib
from resources import RESOURCES as ROUTES
import getpass

DEFAULT_MAX_SERVER = 'http://localhost'
DEFAULT_OAUTH_SERVER = 'https://oauth-test.upc.edu'
DEFAULT_SCOPE = 'widgetcli'
DEFAULT_GRANT_TYPE = 'password'
DEFAULT_CLIENT_ID = 'MAX'


class MaxClient(object):

    def __init__(self,
                 url=DEFAULT_MAX_SERVER,
                 oauth_server=DEFAULT_OAUTH_SERVER,
                 actor=None,
                 auth_method='oauth2',
                 scope=DEFAULT_SCOPE,
                 grant_type=DEFAULT_GRANT_TYPE,
                 client_id=DEFAULT_CLIENT_ID):
        """
        """
        #Strip ending slashes, as all routes begin with a slash
        self.url = url.rstrip('/')
        self.oauth_server = oauth_server.rstrip('/')
        self.setActor(actor)
        self.auth_method = auth_method
        self.scope = scope
        self.grant_type = grant_type
        self.client_id = client_id

    def login(self, username='', password=False):
        if not username:
            username = raw_input("Username: ")
        if not password:
            password = getpass.getpass()

        self.setActor(username)
        return self.getToken(username, password)

    def getToken(self, username, password):
        payload = {"grant_type": self.grant_type,
                   "client_id": self.client_id,
                   "scope": self.scope,
                   "username": username,
                   "password": password
                   }

        req = requests.post('{0}/token'.format(self.oauth_server), data=payload, verify=False)
        response = json.loads(req.text)
        if req.status_code == 200:
            self.token = response.get("access_token", False)
            # Fallback to legacy oauth server
            if not self.token:
                self.token = response.get("oauth_token")
            return self.token
        else:
            raise AttributeError("Bad username or password.")

    def setActor(self, actor, type='person'):
        self.actor = actor and dict(objectType='person', username=actor) or None

    def setToken(self, oauth2_token):
        """
        """
        self.token = oauth2_token

    def setBasicAuth(self, username, password):
        """
        """
        self.ba_username = username
        self.ba_password = password

    def OAuth2AuthHeaders(self):
        """
        """
        headers = {
            'X-Oauth-Token': self.token,
            'X-Oauth-Username': self.actor['username'],
            'X-Oauth-Scope': self.scope,
        }
        return headers

    def BasicAuthHeaders(self):
        """
        """
        auth = (self.ba_username, self.ba_password)
        return auth

    def HEAD(self, route, qs=''):
        """
        """
        headers = {}
        resource_uri = '%s%s' % (self.url, route)
        if qs:
            resource_uri = '%s?%s' % (resource_uri, qs)
        if self.auth_method == 'oauth2':
            headers.update(self.OAuth2AuthHeaders())
            req = requests.head(resource_uri, headers=headers, verify=False)
        elif self.auth_method == 'basic':
            req = requests.head(resource_uri, auth=self.BasicAuthHeaders(), verify=False)
        else:
            raise

        isOk = req.status_code == 200
        if isOk:
            response = int(req.headers.get('X-totalItems', '0'))
        else:
            print req.status_code
            response = ''
        return (isOk, req.status_code, response)

    def GET(self, route, qs=''):
        """
        """
        headers = {}
        resource_uri = '%s%s' % (self.url, route)
        if qs:
            resource_uri = '%s?%s' % (resource_uri, qs)
        if self.auth_method == 'oauth2':
            headers.update(self.OAuth2AuthHeaders())
            req = requests.get(resource_uri, headers=headers, verify=False)
        elif self.auth_method == 'basic':
            req = requests.get(resource_uri, auth=self.BasicAuthHeaders(), verify=False)
        else:
            raise

        isOk = req.status_code == 200
        isJson = 'application/json' in req.headers.get('content-type', '')
        if isOk:
            response = isJson and json.loads(req.content) or None
        else:
            print req.status_code
            response = ''
        return (isOk, req.status_code, response)

    def POST(self, route, query={}):
        """
        """
        headers = {}
        resource_uri = '%s%s' % (self.url, route)
        json_query = json.dumps(query)

        if self.auth_method == 'oauth2':
            headers.update(self.OAuth2AuthHeaders())
            headers.update({'content-type': 'application/json'})
            req = requests.post(resource_uri, data=json_query, headers=headers, verify=False)
        elif self.auth_method == 'basic':
            req = requests.post(resource_uri, data=json_query, auth=self.BasicAuthHeaders(), verify=False)
        else:
            raise

        isOk = req.status_code in [200, 201] and req.status_code or False
        isJson = 'application/json' in req.headers.get('content-type', '')
        if isOk:
            response = isJson and json.loads(req.content) or None
        else:
            print req.status_code
            response = ''

        return (isOk, req.status_code, response)

    def PUT(self, route, query={}):
        """
        """
        headers = {}
        resource_uri = '%s%s' % (self.url, route)
        json_query = json.dumps(query)

        if self.auth_method == 'oauth2':
            headers.update(self.OAuth2AuthHeaders())
            req = requests.put(resource_uri, data=json_query, headers=headers, verify=False)
        elif self.auth_method == 'basic':
            req = requests.put(resource_uri, data=json_query, auth=self.BasicAuthHeaders(), verify=False)
        else:
            raise

        isOk = req.status_code in [200, 201] and req.status_code or False
        isJson = 'application/json' in req.headers.get('content-type', '')
        if isOk:
            response = isJson and json.loads(req.content) or None
        else:
            print req.status_code
            response = ''

        return (isOk, req.status_code, response)

    ###########################
    # USERS
    ###########################

    def addUser(self, username, **kwargs):
        """
        """
        route = ROUTES['user']['route']

        query = {}
        rest_params = dict(username=username)
        valid_properties = ['displayName']
        query = dict([(k, v) for k, v in kwargs.items() if k in valid_properties])

        return self.POST(route.format(**rest_params), query)

    def modifyUser(self, username, properties):
        """
        """
        route = ROUTES['user']['route']

        query = properties
        rest_params = dict(username=username)

        return self.PUT(route.format(**rest_params), query)

    ###########################
    # ACTIVITIES
    ###########################

    def addActivity(self, content, otype='note', contexts=[]):
        """
        """
        route = ROUTES['user_activities']['route']
        query = dict(object=dict(objectType=otype,
                                 content=content,
                                 ),
                     )
        if contexts:
            query['contexts'] = []
            for context in contexts:
                query['contexts'].append(dict(url=context, objectType='context'))

        rest_params = dict(username=self.actor['username'])

        (success, code, response) = self.POST(route.format(**rest_params), query)
        return response

    def getActivity(self, activity):
        """
        """
        route = ROUTES['activity']['route']
        rest_params = dict(activity=activity)
        (success, code, response) = self.GET(route.format(**rest_params))
        return response

    def getUserTimeline(self):
        """
        """
        route = ROUTES['timeline']['route']
        rest_params = dict(username=self.actor['username'])
        (success, code, response) = self.GET(route.format(**rest_params))
        return response

    def getContextActivities(self, context, count=False):
        """ Return the activities given a context
        """
        route = ROUTES['context_activities']['route']
        rest_params = dict(hash=context)

        params = {}
        if context:
            params['qs'] = 'context={}'.format(context)

        if count:
            (success, code, response) = self.HEAD(route.format(**rest_params), **params)
        else:
            (success, code, response) = self.GET(route.format(**rest_params), **params)
        return response

    def getUserActivities(self, context=None, count=False, username=None):
        """ Return all the user activities under a specific context or globally
            if not specified.

            It can be invoked as admin, if an username of the actor is supplied.
        """
        route = ROUTES['user_activities']['route']
        rest_params = dict(username=username if username is not None else self.actor['username'])

        params = {}
        if context:
            params['qs'] = 'context={}'.format(context)

        if count:
            (success, code, response) = self.HEAD(route.format(**rest_params), **params)
        else:
            (success, code, response) = self.GET(route.format(**rest_params), **params)
        return response

    def getTimelineLastAuthors(self, limit=None):
        """
        """
        route = ROUTES['timeline_authors']['route']
        rest_params = dict(username=self.actor['username'])

        params = {}
        if limit:
            params['qs'] = 'limit={}'.format(limit)

        (success, code, response) = self.GET(route.format(**rest_params), **params)
        return response

    def getContextLastAuthors(self, context, limit=None):
        """
        """
        route = ROUTES['context_activities_authors']['route']
        rest_params = dict(hash=context)

        params = {}
        if limit:
            params['qs'] = 'limit={}'.format(limit)

        (success, code, response) = self.GET(route.format(**rest_params), **params)
        return response

    def getAllActivities(self, count=False):
        """ Stats only endpoint, return the aggregation of all user activities """
        route = ROUTES['activities']['route']

        if count:
            (success, code, response) = self.HEAD(route)
        else:
            (success, code, response) = self.GET(route)
        return response

    def getAllComments(self, count=False):
        """ Stats only endpoint, return the aggregation of all user activities """
        route = ROUTES['comments']['route']

        if count:
            (success, code, response) = self.HEAD(route)
        else:
            (success, code, response) = self.GET(route)
        return response

    ###########################
    # COMMENTS
    ###########################

    def addComment(self, content, activity, otype='comment'):
        """
        """
        route = ROUTES['comments']['route']
        query = dict(actor=self.actor,
                     object=dict(objectType=otype,
                                 content=content,
                                 ),
                     )
        rest_params = dict(activity=activity)
        (success, code, response) = self.POST(route.format(**rest_params), query)
        return response

    def getComments(self, activity):
        """
        """
        route = ROUTES['comments']['route']
        rest_params = dict(activity=activity)
        (success, code, response) = self.GET(route.format(**rest_params))

    ###########################
    # SUBSCRIPTIONS & CONTEXTS
    ###########################

    def addContext(self, param_value, displayName, permissions=None, context_type='context', param_name='url'):
        """
        """
        route = ROUTES['contexts']['route']

        query = {param_name: param_value,
                 'objectType': context_type,
                 'displayName': displayName,
                 'permissions': permissions
                 }

        if permissions:
            query['permissions'].update(permissions)

        (success, code, response) = self.POST(route, query)
        return response

    def subscribe(self, url, otype='context', username=None):
        """
        """
        route = ROUTES['subscriptions']['route']

        query = dict(object=dict(objectType=otype,
                                 url=url,
                                 ),
                     )
        rest_params = dict(username=username is not None and username or self.actor['username'])

        (success, code, response) = self.POST(route.format(**rest_params), query)
        return response

    # def unsubscribe(self,username,url,otype='service'):
    #     """
    #     """

    def subscribed(self):
        """
        """
        route = ROUTES['subscriptions']['route']

        rest_params = dict(username=self.actor['username'])

        (success, code, response) = self.GET(route.format(**rest_params))
        return response

    def examplePOSTCall(self, username):
        """
        """
        route = ROUTES['']['route']

        query = {}
        rest_params = dict(username=username)

        (success, code, response) = self.POST(route.format(**rest_params), query)
        return response

    def exampleGETCall(self, param1, param2):
        """
        """
        route = ROUTES['']['route']
        rest_params = dict(Param1=param1)
        (success, code, response) = self.GET(route.format(**rest_params))
        return response

    # def follow(self,username,oid,otype='person'):
    #     """
    #     """

    # def unfollow(self,username,oid,otype='person'):
    #     """
    #     """

    ###########################
    # ADMIN
    ###########################

    def getUsers(self):
        """
        """
        route = ROUTES['admin_users']['route']
        (success, code, response) = self.GET(route)
        return response

    def getActivities(self):
        """
        """
        route = ROUTES['admin_activities']['route']
        (success, code, response) = self.GET(route)
        return response

    def getContexts(self):
        """
        """
        route = ROUTES['admin_contexts']['route']
        (success, code, response) = self.GET(route)
        return response

    def getSecurity(self):
        route = ROUTES['admin_security']['route']
        resource_uri = '%s%s' % (self.url, route)
        req = requests.get(resource_uri, verify=False)
        isOk = req.status_code == 200
        isJson = 'application/json' in req.headers.get('content-type', '')
        if isOk:
            response = isJson and json.loads(req.content) or None
        return response
