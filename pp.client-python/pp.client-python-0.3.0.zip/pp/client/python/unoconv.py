################################################################
# pp.client - Produce & Publish Python Client
# (C) 2013, ZOPYX Ltd, Tuebingen, Germany
################################################################

""" XMLRPC client to access the unoconv API of the Produce & Publish server """

import os
import base64
import plac
import json
try:
    from urllib2 import URLError
except ImportError:
    from urllib.error import URLError
import requests
from pp.client.python.logger import getLogger
from pp.client.python.util import mask_url

@plac.annotations(
    input_filename=('Source file to be converted', 'positional'),
    format=('Output format (default=pdf)', 'option', 'f'),
    output=('Write converted file to custom filename', 'option', 'o'),
    server_url=('URL of Produce & Publish server)', 'option', 's'),
    async=('Perform conversion asynchronously)', 'flag', 'a'),
    verbose=('Verbose mode)', 'flag', 'v'),
)
def unoconv(input_filename, 
           format='pdf', 
           output='',
           async=False, 
           server_url='http://localhost:6543',
           verbose=False):

    LOG = getLogger(1 if verbose else 0)
    server_url = server_url.rstrip('/') + '/api/1/unoconv'

    params = dict(output_format=format, filename=input_filename, async=int(async))
    files = {'file': open(input_filename, 'rb')}
    LOG.debug('Sending data to {0:s} ({1:d} bytes)'.format(mask_url(server_url), 
                                                     os.path.getsize(input_filename)))
    result = requests.post(server_url, data=params, files=files)
    if result.status_code != 200:
        raise urllib2.URLError('Error calling {0:s} (Status: {1:d})'.format(mask_url(server_url), result.status_code))
    result = json.loads(result.text)

    if async:
        LOG.debug(result)
        return result
    else:
        if result['status'] == 'OK':
            if not output:
                base, ext = os.path.splitext(input_filename)
                output= base + '.' + format
            with open(output, 'wb') as fp:
                fp.write(base64.decodestring(result['data'].encode('ascii')))
            LOG.debug('Output filename: {0:s}'.format(output))
        else:
            LOG.debug('An error occured')
            LOG.debug('Output:')
            LOG.debug(result['output'])
        return result

def main():
    plac.call(unoconv)

if __name__ == '__main__':
    main()
