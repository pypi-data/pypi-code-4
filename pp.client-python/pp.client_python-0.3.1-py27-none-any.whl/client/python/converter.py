################################################################
# pp.client - Produce & Publish Python Client
# (C) 2013, ZOPYX Ltd, Tuebingen, Germany
################################################################

import plac
import base64
import json
import time
import requests
from pp.client.python.logger import getLogger

@plac.annotations(
    server_url=('URL of Produce & Publish API)', 'option', 's'),
)
def available_converters(server_url='http://localhost:6543/api'):
    return requests.get(server_url + '/converters')

def main():
    print plac.call(available_converters)

if __name__ == '__main__':
    main()
