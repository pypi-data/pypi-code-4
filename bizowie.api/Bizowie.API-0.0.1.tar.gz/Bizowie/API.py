"""Bizowie API Acesss

General Doc: http://bizowie.com/api/

Sample usage:

        import Bizowie.API
        aapi = Bizowie.API.API("bizowie.site.bizowie.com", "api_key", "secret_key")
        aapi.call('tickets/add_comment/1003', { 'comment':'woo' } )

"""
              
import requests
import json

__author__ = "Michael Flickinger"
__version__ = "0.0.1"

class API:
    def __init__(self, site, api_key, api_secret_key
	):
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        self.site = site

    def call(self, api_command, args):
	"""
        Make a Bizowie system request.
        """
        payload = {
            'request': json.dumps(args),
            'api_key': self.api_key,
            'secret_key': self.api_secret_key,
            'site': self.site,
        }

        response = requests.post(
                url='https://' + self.site + '/bz/api/' + api_command,
                data = payload
            )

        r_json = response.content
        r = json.loads(r_json)

        if r.get('error', None) is not None:
            raise ValueError(r.get('error', None))

        return r


