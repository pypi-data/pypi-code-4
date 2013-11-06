import posixpath

from notmm.utils.wsgilib import HTTPResponse

from .configuration import settings

def image_handler(request, *args, **kwds):
    #print args, kwds
    docroot = kwds.get('document_root', settings.MEDIA_ROOT)
    filename = posixpath.split(request.path_url)[-1]
    ext = filename.split('.')[-1]
    content_type = "image/%s" % ext
    
    filename = posixpath.join(docroot, filename)
    try:
        fdata = open(filename, 'rb').read()
    except (IOError,OSError):
        # TODO: Log exception if an error occured reading the file
        fdata = str()

    headers = (
        ('Content-Type', content_type),
        ('Content-Length', str(len(fdata)))
        )
    return HTTPResponse(content=fdata, headers=headers, force_unicode=False)

