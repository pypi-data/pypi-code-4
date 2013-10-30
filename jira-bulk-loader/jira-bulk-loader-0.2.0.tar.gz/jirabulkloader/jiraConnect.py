
import requests
import re

class JiraConnect:
    """The class handles low level interaction with JIRA (such as 
    HTTP connection, authentication, GET, POST, PUT, DELETE requests)
    as well as connection and HTTP errors and exception"""

    def __init__(self, hostname, username = '', password = '', api_version = 2):
        self.jira_url = '/'.join([self._validate_url_and_type(hostname), 'rest/api', str(api_version)])

        self.session = requests.Session()
        if username: self.session.auth = (username, password)
        self.session.headers = { 'content-type': 'application/json' }

        self.jira_ok_codes = [requests.codes.ok, requests.codes.created, requests.codes.no_content] # 200, 201, 204

    def _validate_url_and_type(self, url):
        match = re.search("^https?://", url)
        return url if match else "http://" + url

    def get(self, action, **kwargs):
        """wrapper for GET request.

        If **kwargs is specified, the list of parameters will be added to the request"""
        action = '/'.join([self.jira_url, action])
        if kwargs:
            params = [key + '=' + kwargs[key] for key in kwargs.keys()]
            action += '?' + '&'.join(params)
        return self._make_request(self.session.get, action)

    def post(self, action, data):
        """wrapper for POST request"""
        return self._make_request(self.session.post, '/'.join([self.jira_url, action]), data)

    def put(self, action, data):
        """wrapper for PUT request"""
        return self._make_request(self.session.put, '/'.join([self.jira_url, action]), data)

    def delete(self):
        """wrapper for DELETE request"""
        return self._make_request(self.session.delete)

    def _make_request(self, method, url, data = None):
        """Make HTTP request

        executes HTTP request and return a tupple (HTTP_status_code, context) if the request
        was successful or raise JiraConnectException if it failed"""
        try:
            r = method(url, data) if data else method(url)
        except requests.RequestException as e:
            raise JiraConnectConnectionError(unicode(e.message) + ': ' + url)
        if r.status_code not in self.jira_ok_codes:
            raise JiraConnectActionError(url, r.status_code, r.text, r.headers)
        return str(r.text)

class JiraConnectConnectionError(RuntimeError):
    """There was an exception that occurred while handling a request"""

class JiraConnectActionError(RuntimeError):
    """There was an exception that occurred while handling a request"""
    def __init__(self, url, code, message, headers):
        self.url = url
        self.code = code
        self.message = message
        self.headers = headers

