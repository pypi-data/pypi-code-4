# coding=utf-8
import json
from urllib import urlencode, urlopen
from main import settings


class VkApiException(Exception):
    def __init__(self, data):
        Exception.__init__(self, data['error']['error_msg'])


class VkApi(object):
    access_token = ''

    def __init__(self):
        self.access_token = settings.VK_ACCESS_TOKEN

    def get_response(self, method, params={}):
        params['access_token'] = self.access_token
        params['v'] = '5.0'
        url = "https://api.vk.com/method/%s?%s" % (method, urlencode(params))
        response = urlopen(url).read()
        data = json.loads(response)

        if 'error' in data:
            raise VkApiException(data)

        return data['response']


    def get_audio(self, id, limit=30, offset=0):
        return self.get_response('audio.get', {
            'count': limit,
            'offset': offset,
            'owner_id': id
        })['items']

    def get_audio_count(self, id):
        return int(self.get_response('audio.getCount', {'owner_id': id}))

    def get_all_tracks(self, id):
        tracks = []
        for offset in range(0, self.get_audio_count(id), 100):
            tracks += self.get_audio(id, 100, offset)
        return tracks