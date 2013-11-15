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
    job_id=('Job id to poll', 'positional'),
    server_url=('URL of Produce & Publish API)', 'option', 's'),
    verbose=('Verbose mode', 'flag', 'v'),
)
def poll(job_id, verbose=False, server_url='http://localhost:6543/api/1/poll'):

    LOG = getLogger(verbose)
    while True:
        time.sleep(1)
        LOG.debug('polling')
        result = requests.get(server_url + '/' + job_id)
        result = json.loads(result.text)
        if result['done']:
            result['status'] = 'OK' if result['status'] == 0 else 'ERROR'
            if result['status'] == 'OK':
                result['data'] = base64.decodestring(result['data'])
            return result    
    return result

def main():
    plac.call(poll)

if __name__ == '__main__':
    main()
