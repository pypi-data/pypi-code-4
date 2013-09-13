from hashlib import sha1
import requests
import json
import urllib
from resources import RESOURCES as ROUTES
import getpass

DEFAULT_MAX_SERVER = 'http://localhost:8081'
DEFAULT_OAUTH_SERVER = 'https://oauth.upcnet.es'
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

    def getActor(self):
        return self.actor.get('username', '')

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
            print 'GET {} - {} - {}'.format(req.status_code, req.content, route)
            response = ''
        return (isOk, req.status_code, response)

    def POST(self, route, query={}, upload_file=None):
        """
        """
        headers = {}
        resource_uri = '%s%s' % (self.url, route)
        json_query = json.dumps(query)

        if upload_file:
            headers.update(self.OAuth2AuthHeaders())
            files = {'file': ('avatar.png', upload_file)}
            req = requests.post(resource_uri, headers=headers, files=files, verify=False)
        else:
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
            print 'POST {} - {} - {}'.format(req.status_code, req.content, route)
            response = req.content

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
            print 'PUT {} - {} - {}'.format(req.status_code, req.content, route)
            response = ''

        return (isOk, req.status_code, response)

    def DELETE(self, route, query={}):
        """
        """
        headers = {}
        resource_uri = '%s%s' % (self.url, route)
        json_query = json.dumps(query)

        if self.auth_method == 'oauth2':
            headers.update(self.OAuth2AuthHeaders())
            headers.update({'content-type': 'application/json'})
            req = requests.delete(resource_uri, data=json_query, headers=headers, verify=False)
        elif self.auth_method == 'basic':
            req = requests.delete(resource_uri, data=json_query, auth=self.BasicAuthHeaders(), verify=False)
        else:
            raise

        isOk = req.status_code in [204] and req.status_code or False
        isJson = 'application/json' in req.headers.get('content-type', '')
        if isOk:
            response = isJson and json.loads(req.content) or None
        else:
            print 'DELETE {} - {} - {}'.format(req.status_code, req.content, route)
            response = req.content

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

    def postAvatar(self, username, image):
        """
        """
        route = ROUTES['avatar']['route']
        rest_params = dict(username=username)

        return self.POST(route.format(**rest_params), upload_file=image)

    ###########################
    # ACTIVITIES
    ###########################

    def addActivity(self, content, otype='note', contexts=[], generator=None, username=None):
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

        if generator:
            query['generator'] = generator

        rest_params = dict(username=username is not None and username or self.actor['username'])

        (success, code, response) = self.POST(route.format(**rest_params), query)
        return (success, code, response)

    def add_activity_as_context(self, content, url, otype='note', generator=None):
        """
        """
        route = ROUTES['context_activities']['route']
        query = dict(object=dict(objectType=otype,
                                 content=content,
                                 ),
                     )

        if generator:
            query['generator'] = generator

        context_hash = sha1(url).hexdigest()
        rest_params = dict(hash=context_hash)

        (success, code, response) = self.POST(route.format(**rest_params), query)
        return (success, code, response)

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

    def deleteContext(self, url):
        """
        """
        route = ROUTES['context']['route']

        context_hash = sha1(url).hexdigest()
        rest_params = dict(hash=context_hash)

        (success, code, response) = self.DELETE(route.format(**rest_params))
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

    def unsubscribe(self, url, otype='context', username=None):
        """ Takes directly the url and calculate the hash
        """
        route = ROUTES['subscription']['route']
        context_hash = sha1(url).hexdigest()

        rest_params = dict(username=username if username is not None else self.actor['username'],
                           hash=context_hash)

        (success, code, response) = self.DELETE(route.format(**rest_params))
        return response

    def subscribed_to_context(self, url):
        """
        """
        route = ROUTES['context_subscriptions']['route']
        context_hash = sha1(url).hexdigest()

        rest_params = dict(hash=context_hash)

        (success, code, response) = self.GET(route.format(**rest_params))
        return response

    def subscribed(self):
        """
        """
        route = ROUTES['subscriptions']['route']

        rest_params = dict(username=self.actor['username'])

        (success, code, response) = self.GET(route.format(**rest_params))
        return response

    ###########################
    # Conversations
    ###########################

    def pushtokens_by_conversation(self, conversation_id):
        """
        """
        route = ROUTES['pushtokens']['route']

        rest_params = dict(id=conversation_id)

        (success, code, response) = self.GET(route.format(**rest_params))
        return (success, code, response)

    ###########################
    # Examples
    ###########################

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
        route = ROUTES['users']['route']
        (success, code, response) = self.GET(route)
        return response

    def getActivities(self):
        """
        """
        route = ROUTES['activities']['route']
        (success, code, response) = self.GET(route)
        return response

    def getContexts(self):
        """
        """
        route = ROUTES['contexts']['route']
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
