################################################################
# pp.client - Produce & Publish Python Client
# (C) 2013, ZOPYX Ltd, Tuebingen, Germany
################################################################

""" XMLRPC client to access the unoconv API of the Produce & Publish server """

import os
import base64
import plac
import json
import requests
from pp.client.python.logger import getLogger

@plac.annotations(
    input_filename=('Source file to be converted', 'positional'),
    format=('Output format (default=pdf)', 'option', 'f'),
    output=('Write converted file to custom filename', 'option', 'o'),
    server_url=('URL of Produce & Publish XMLRPC API)', 'option', 's'),
    async=('Perform conversion asynchronously)', 'flag', 'a'),
    verbose=('Verbose mode)', 'flag', 'v'),
)
def unoconv(input_filename, 
           format='pdf', 
           output='',
           async=False, 
           server_url='http://localhost:6543/api/1/unoconv',
           verbose=False):

    LOG = getLogger(1 if verbose else 0)

    params = dict(output_format=format, filename=input_filename)
    files = {'file': open(input_filename, 'rb')}
    LOG.debug('Sending data to {} ({} bytes)'.format(server_url, os.path.getsize(input_filename)))
    result = requests.post(server_url, data=params, files=files)
    result = json.loads(result.text)

    if async:
        LOG.debug(result)
    else:
        if result['status'] == 'OK':
            if not output:
                base, ext = os.path.splitext(input_filename)
                output= base + '.' + format
            with open(output, 'wb') as fp:
                fp.write(base64.decodestring(result['data']))
            LOG.debug('Output filename: {}'.format(output))
        else:
            LOG.debug('An error occured')
            LOG.debug('Output:')
            LOG.debug(result['output'])

    return result

def main():
    plac.call(unoconv)

if __name__ == '__main__':
    main()
