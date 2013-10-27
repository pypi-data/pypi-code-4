#!/usr/bin/env python
#coding=utf-8

import re
import json
import gecimi
import requests


__version__ = '0.0.1'

match = re.compile(r'\([^)]*?\)|（[^）]*?）')


class LastLyric(object):

    api_key = ''

    def __init__(self, api_key=None):
        self.api_key = self.api_key or api_key

    def getLast(self, user):
        url = ('http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks'
               '&user=%s&api_key=%s&format=json' % (user, self.api_key))
        try:
            r = requests.get(url, verify=False, stream=False, timeout=10)
            content = r.content
        except Exception, e:
            print e
            content = '{}'
        try:
            result = json.loads(content)
            song = result['recenttracks']['track'][0]
        except Exception, e:
            print e
            return ''
        artist = song['artist']['#text']
        title = song['name']
        title = match.sub('', title)
        if artist:
            lyric = gecimi.Lyric(title, artist)
            lrc = lyric.get()
        else:
            lyric = gecimi.Lyric(title)
            lrc = lyric.get()
        return lrc


if __name__ == '__main__':
    api_key = ''
    lyric = LastLyric(api_key)
    print lyric.getLast('jht360')
