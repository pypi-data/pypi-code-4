import json
import urllib2
import hashlib

from dbs.gameanalytics import conf


class GameAnalytics(object):
    @classmethod
    def configure(cls, **kwargs):
        for key, value in kwargs.iteritems():
            if hasattr(conf, key):
                setattr(conf, key, value)

    @classmethod
    def design(cls, **kwargs):
        cls.log(category='design', **kwargs)

    @classmethod
    def quality(cls, **kwargs):
        cls.log(category='quality', **kwargs)

    @classmethod
    def business(cls, **kwargs):
        cls.log(category='business', **kwargs)

    @classmethod
    def user(cls, **kwargs):
        cls.log(category='user', **kwargs)

    @classmethod
    def log(cls, category=None, user_id=None, session_id=None, **kwargs):
        message = {
            'user_id': user_id,
            'session_id': session_id,
            'build': conf.build,
        }
        message.update(kwargs)

        json_message = json.dumps(message)
        digest = hashlib.md5()
        digest.update(json_message)

        digest.update(conf.secret_key)
        json_authorization = {'Authorization': digest.hexdigest()}

        url = "%s/%s/%s/%s" % (
            conf.endpoint_url, conf.api_version, conf.game_key, category)

        request = urllib2.Request(url, json_message, json_authorization)

        try:
            response = urllib2.urlopen(request)
        except urllib2.HTTPError, e:
            response = e.read()

        return response
