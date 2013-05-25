#!/usr/bin/python
import requests


class Lmgtfy:
    def lmgtfy_url(self, query):
        return 'http://lmgtfy.com/?q=' + '+'.join([word.replace(" ", "+") for word in query])

    def short_url(self, query):
        payload = {'format': 'json', 'url': self.lmgtfy_url(query)}
        r = requests.get('http://is.gd/create.php', params=payload)
        return r.json()['shorturl']
