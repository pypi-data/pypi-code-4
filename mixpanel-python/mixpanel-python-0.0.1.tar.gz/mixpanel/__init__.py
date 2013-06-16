"""Based on mixpanel example code from:
https://mixpanel.com/docs/integration-libraries/python

Requires `curl`, simplejson, and Python version 2.4 or higher.  mixpanel-python is intended
to be simpler than https://pypi.python.org/pypi/mixpanel which has more
dependencies, like beanstalkd
"""
import base64
import datetime
import logging
import simplejson
import subprocess
import unittest


class Mixpanel(object):
    MIXPANEL_BASE_URL = "https://api.mixpanel.com"

    # Flip this switch to no-op and skip actually sending events to the
    # mixpanel api.  Useful in dev/test environments.
    SKIP_API_CALLS = False

    def __init__(self, api_key, api_token):
        super(Mixpanel, self).__init__()
        self.api_key = api_key
        self.api_token = api_token
        self.debug = False

    def call_mixpanel(self, url, params):
        """
        A simple function for asynchronously calling to the mixpanel.com API.
        This function requires `curl` and Python version 2.4 or higher.

        @return Instance of L{subprocess.Popen}

        If you want to block until this call returns, you can call
        .communicate() on the returned object.
        """
        if self.SKIP_API_CALLS:
            logging.debug("skipping mixpanel api call: %s %" % (url, params))
            return

        data = base64.b64encode(simplejson.dumps(params))
        request = url + "?api_key=%s&data=%s" % (self.api_key, data)

        # It seems that mixpanel recommends opening a curl subprocess as an
        # easy way to make this async here:
        # https://mixpanel.com/docs/integration-libraries/python
        if self.debug:
            logging.info("%s %s" % (url, params))
            logging.info(request)
        return subprocess.Popen(("curl", request), stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE)

    def track_event(self, event, properties):
        """
        @param event: The overall event/category you would like to log this data under
        @param properties: A dictionary of key-value pairs that describe the event
                           See https://mixpanel.com/api/ for further detail.

        Example usage:
        track("invite-friends",
                 {"method": "email", "number-friends": "12", "ip": "123.123.123.123"})
        """

        if "token" not in properties:
            properties["token"] = self.api_token

        params = {
            "event": event,
            "properties": properties
        }
        url = "%s/track/" % self.MIXPANEL_BASE_URL

        return self.call_mixpanel(url, params)

    def import_event(self, event, properties):
        """
        @param event: The overall event/category you would like to log this data under
        @param properties: A dictionary of key-value pairs that describe the event
                           See https://mixpanel.com/api/ for further detail.

        See also:
        https://mixpanel.com/docs/api-documentation/importing-events-older-than-31-days

        * this method lets you import events older than 5 days
        * The endpoint is /import/ instead of /track/
        * As an added level of security, you must include your API key as a
        parameter outside the Base64. Do not confuse your API Key with your
        project token.
        * If you are importing event or property names that have not been sent
        yet through the regular /track endpoint, they won't show up in the
        Mixpanel interface. They need to have been sent through that endpoint
        durring the last thirty days in order to be loaded by the interface. In
        order to avoid this, you need to send each event (with all the possible
        property names -- the values don't matter) at least once through the
        normal /track endpoint if you are not already sending them as part of
        your day to day intergration.

        Example usage:
        import_event({'event': '$signup',
                      'properties': {'distinct_id': 481,
                                     'time': 1321499371,
                                     'token': '35efee6b32cfab9852a4cddb4d9c710e'}})
        """

        if "token" not in properties:
            properties["token"] = self.api_token

        params = {"event": event, "properties": properties}
        url = "%s/import/" % self.MIXPANEL_BASE_URL
        return self.call_mixpanel(url, params)

    def track_or_import_event(self, event, properties):
        """
        Smart method will correctly call either /track or /import based on the
        'time' value from the event properties
        """
        ts = properties.get('time')
        if ts:
            dt = datetime.datetime.fromtimestamp(ts)
            now = datetime.datetime.utcnow()
            five_days_ago = now - datetime.timedelta(days=5)
            if dt < five_days_ago:
                return self.import_event(event, properties)

        return self.track_event(event, properties)

    def engage_user_set(self, user_id, properties):
        """
        Set properties on a user. If you are incrementing a value,
        use the engage_add method.
        https://mixpanel.com/docs/people-analytics/people-http-specification-insert-data
        """
        params = {
            "$set": properties,
            "$token": self.api_token,
            "$distinct_id": user_id
        }
        url = "%s/engage/" % self.MIXPANEL_BASE_URL
        return self.call_mixpanel(url, params)

    def engage_user_increment(self, user_id, properties):
        """
        This method is used to set increment properties on a user.
        https://mixpanel.com/docs/people-analytics/people-http-specification-insert-data
        """
        params = {
            "$add": properties,
            "$token": self.api_token,
            "$distinct_id": user_id
        }
        url = "%s/engage/" % self.MIXPANEL_BASE_URL
        return self.call_mixpanel(url, params)


class MixpanelTest(unittest.TestCase):
    """
    To be run with:
        nosetests mixpanel.py
    """
    def setUp(self):
        # mock the supbrocess module, so we don't actually make calls to
        # mixpanel via HTTP
        class MockedSubprocess():
            PIPE = None

            @classmethod
            def Popen(klass, *args, **kwargs):
                return klass

            @classmethod
            def communicate(klass, *args, **kwargs):
                return ("1", "")

        global subprocess
        self.subprocess_module = subprocess
        subprocess = MockedSubprocess
        self.mp = Mixpanel("some_api_key", "some_api_token")

    def tearDown(self):
        global subprocess
        subprocess = self.subprocess_module

    def test_track_event(self):
        sp = self.mp.track_event("some_event", {"property": "val"})
        self.assertEqual(sp.communicate()[0], "1")  # mixpanel API just returns "1" in body

        # expect error when trying to serialize datetime
        try:
            self.mp.track_event("some_event", {"property": datetime.datetime.now()})
        except Exception, e:
            self.assertEqual(type(e), TypeError)

    def test_import_event(self):
        sp = self.mp.import_event("some_event", {"property": "val"})
        self.assertEqual(sp.communicate()[0], "1")  # mixpanel API just returns "1" in body

    def test_track_or_import_event(self):
        sp = self.mp.track_or_import_event("some_event", {"property": "val"})
        self.assertEqual(sp.communicate()[0], "1")  # mixpanel API just returns "1" in body
