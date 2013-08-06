"""Event Fabric API Client Library"""
from __future__ import print_function

import sys
import json

try:
    import requests
except ImportError:
    print("Couldn't import requests library")
    print("Install it with 'pip install requests' and try again")
    sys.exit(-1)

class Client(object):
    """API Client"""
    def __init__(self, username, password,
            root_url="https://event-fabric.com/api/"):
        self.root_url = root_url if root_url.endswith("/") else root_url + "/"
        self.username = username
        self.password = password
        self.cookies = None

    def login(self, requester=requests.post):
        """login to the service with the specified credentials, return a tuple
        with a boolean specifying if the login was successful and the response
        object"""
        headers = {'content-type': 'application/json'}
        response = requester(self.endpoint("session"),
                data=json.dumps(self.credentials), headers=headers)

        self.cookies = response.cookies

        status_ok = response.status_code in (200, 201)
        return status_ok, response

    @property
    def credentials(self):
        """get credentials information"""
        return {
                "username": self.username,
                "password": self.password
        }

    def endpoint(self, path):
        """return the service endpoint for path"""
        return self.root_url + path

    def send_event(self, event, requester=requests.post):
        """send event to server, return a tuple with a boolean specifying if
        the login was successful and the response object"""
 
        headers = {'content-type': 'application/json'}
        response = requester(self.endpoint("event"),
                data=json.dumps(event.json), cookies=self.cookies,
                headers=headers)

        status_ok = response.status_code in (200, 201)
        return status_ok, response

class Event(object):
    """an object representing an event to be sent to the server,
    
    value is a free form json value that contains the information from
    the event.
    channel is a string with the name that identifies this kind of events
    username is the logged in username"""

    def __init__(self, value, channel):

        self.value = value
        self.channel = channel

    @property
    def json(self):
        """return a json representation of the object"""
        return {"value": self.value, "channel": self.channel}

    def __str__(self):
        return json.dumps(self.json)
