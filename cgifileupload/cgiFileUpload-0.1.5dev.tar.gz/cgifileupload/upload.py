'''Functionality for uploading image files.

see http://webpython.codepoint.net/cgi_file_upload
and http://webpython.codepoint.net/cgi_big_file_upload
'''
import os
import tg
import logging
from image_reduce import scale_image

log = logging.getLogger(__name__)

CHUNK = 100000

def fbuffer(f, chunk_size=CHUNK):
    '''
    a generator to buffer file chunks
    '''
    while True:
        chunk = f.read(chunk_size)
        if not chunk: break
        yield chunk


def writefile(filecontent, filename, filepath, scale=False):
    '''
    Takes a `FieldStorage` type (the result from an html fileupload)
    and writes it to disk.

    Notice that as a file could (potentially) be large the file is
    written to the server's disk in chunks (controlled by CHUNK).
    eg A 3MB file will be written in 30 or so chunks.

    :param instance filecontent:  a FieldStorage instance
    :param str filename:
    :param str filepath:  full path to save directory
    '''

    f = os.path.join(filepath, filename)
    fh = open(f, 'wb', CHUNK)

    # read the file in chunks
    for chunk in fbuffer(filecontent.file):
        fh.write(chunk)

    fh.close()

    if scale:
        # and once written we want to open it with PIL/Image 
        # and scale pyit if it's too big...
        scale_image(f)




