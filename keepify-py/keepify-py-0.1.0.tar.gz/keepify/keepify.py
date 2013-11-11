import base64
import json
import urllib
import urllib2

'''
The keepify package allows you to track events from your python application.

The Keepify class is the primary class for tracking events

The Consumer class allows callers to customize the IO characteristics of their tracking.
'''

VERSION = '0.1.0'

class Keepify(object):
    '''
    Use instances of Keepify to track events from your python code.
    '''

    def __init__(self, token, consumer=None):
        """
        Creates a new Keepify object, which can be used for all tracking.

        To use keepify, create a new Keepify object using your
        token.  Takes in a user token and an optional Consumer (or
        anything else with a send() method). If no consumer is
        provided, Keepify will use the default Consumer, which
        communicates one synchronous request for every message.
        """
        self._token = token
        self._consumer = consumer or Consumer()

    def track(self, user_id, event_name, properties={}):
        """
        Notes that an event has occurred, along with a user_id (a unique user identifier such user email),
        an event name describing the event and a set of properties
        describing that event. Properties are provided as a Hash with
        string keys and strings, numbers or booleans as values.

          # Track that user "example_user@example.com"'s credit card was declined
          mp.track("example_user@example.com", "Credit Card Declined")

          # Properties describe the circumstances of the event,
          # or aspects of the source or user associated with the event
          mp.track("example_user@example.com", "Welcome Email Sent", {
              'Email Template' => 'Pretty Pink Welcome',
              'User Sign-up Cohort' => 'July 2013'
          })
        """
        all_properties = {
            'kpusr' : self._token,
            'kpuid': user_id,
            'kplib': 'python',
            'kplibversion': VERSION,
        }
        all_properties.update(properties)
        self._consumer.send(all_properties)

class KeepifyException(Exception):
    '''
    KeepifyExceptions will be thrown if the server can't recieve
    our events or updates for some reason- for example, if we can't
    connect to the Internet.
    '''
    pass

class Consumer(object):
    '''
    The simple consumer sends an HTTP request directly to the Keepify service,
    with one request for every call.
    '''
    def __init__(self, events_url=None):
        self._request_url = 'http://analytics.keepify.com/kpy.png'

    def send(self, json_message):
        '''
        Record an event or a profile update. Send is the only method
        associated with consumers. Will raise an exception if the endpoint
        doesn't exist, if the server is unreachable or for some reason
        can't process the message.

        :param json_message: A json message formatted for the endpoint.
        :type json_message: str
        :raises: KeepifyException
        '''
        self._write_request(self._request_url, json_message)

    def _write_request(self, request_url, json_message):
        data = urllib.urlencode(json_message)
        try:
            response = urllib2.urlopen(request_url + '?' + data).read()
        except urllib2.HTTPError as e:
            raise KeepifyException(e)

        return True