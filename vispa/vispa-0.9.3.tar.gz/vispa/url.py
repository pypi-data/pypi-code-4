import re
import os
import vispa

def clean(url):
    u = url.replace(u'\\',u'/').replace(u'///',u'/').strip()
    return re.sub(u'(?<!:)//', u'/', u)

def join(*args):
    return clean(u'/'.join(args))

def dynamic(*args, **kwargs):
    base_dynamic = vispa.config(u'web', u'base.dynamic', None) or vispa.config(u'web', u'base', u'/')
    url = join(base_dynamic, *args)
    encoding = kwargs.get('encoding', None)
    if encoding:
        return url.encode(encoding)
    else:
        return url

def static(*args,  **kwargs):
    relative_url = join(*args)
    base_static = vispa.config(u'web', u'base.static', None) or vispa.config(u'web', u'base', u'/')

    if relative_url.startswith('/'):
        relative_url = relative_url[1:]

    if kwargs.get('staticdir', True):
        relative_url = join(u'static', relative_url)

    extension = kwargs.get('extension', None)
    if extension:
        relative_url = join(u'extensions', extension, relative_url)

    url = join(base_static, relative_url)
    if kwargs.get('timestamp', True):
        path = join(u'vispa', relative_url)
        try:
            t = os.path.getmtime(vispa.codepath(path))
        except:
            t = 0
        url = u'%s?%s' % (url, unicode(t))
    
    encoding = kwargs.get('encoding', None)
    if encoding:
        return url.encode(encoding)
    else:
        return url
