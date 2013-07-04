################################################################
# pp.client - Produce & Publish Python Client
# (C) 2013, ZOPYX Ltd, Tuebingen, Germany
################################################################

import os
import plac
import json
import time
import base64
import requests
import tempfile
import zipfile
import xmlrpclib
from pp.client.python.logger import getLogger
from pp.client.python.poll import poll

def makeZipFromDirectory(directory):
    """ Generate a ZIP file from a directory containing all its
        contents. Returns the filename of the generated ZIP file.
    """

    directory = os.path.abspath(directory)
    if not os.path.exists(directory):
        raise IOError('Directory {} does not exist'.format(directory))
    zip_filename = tempfile.mktemp()
    ZF = zipfile.ZipFile(zip_filename, 'w')
    for dirname, dirnames, filenames in os.walk(directory):
        for fname in filenames:
            arcname = os.path.join(dirname, fname).replace(directory + os.path.sep, '')
            fullname = os.path.abspath(os.path.join(dirname, fname))
            ZF.write(fullname, arcname)
    ZF.close()
    return zip_filename

@plac.annotations(
    source_directory=('Source directory containing content and assets to be converted', 'positional'),
    converter=('PDF converter to be used (princexml, pdfreactor)', 'option', 'c'),
    output=('Write result ZIP to given .zip filename', 'option', 'o'),
    server_url=('URL of Produce & Publish XMLRPC API)', 'option', 's'),
    async=('Perform conversion asynchronously)', 'flag', 'a'),
    verbose=('Verbose mode', 'flag', 'v'),
)
def pdf(source_directory,
        converter='princexml', 
        output='',
        async=False, 
        server_url='http://localhost:6543/api/1/pdf',
        verbose=False):

    LOG = getLogger(debug=1 if verbose else 0)

    zip_filename = makeZipFromDirectory(source_directory)
    params = dict(converter=converter, async=int(async))
    files = {'file': open(zip_filename, 'rb')}
    LOG.debug('Sending data to {} ({}, {} bytes)'.format(server_url, converter, os.path.getsize(zip_filename)))
    result = requests.post(server_url, data=params, files=files)
    result = json.loads(result.text)
    os.unlink(zip_filename)
    
    if async:
        LOG.debug(result)
        return result
    else:        
        if result['status'] == 'OK':
            if not output:
                base, ext = os.path.splitext(zip_filename)
                output= base + '.pdf'
            with open(output, 'wb') as fp:
                fp.write(base64.decodestring(result['data']))
            LOG.debug('Output filename: {}'.format(output))
        else:
            LOG.debug('An error occured')
            LOG.debug('Output:')
            LOG.debug(result['output'])
        return result
    
def main():
    plac.call(pdf)

if __name__ == '__main__':
    main()
