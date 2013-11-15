################################################################
# pp.client - Produce & Publish Python Client
# (C) 2013, ZOPYX Ltd, Tuebingen, Germany
################################################################

import urlparse

def mask_url(url):
    parts = list(urlparse.urlparse(url))
    netloc = parts[1]
    if '@' in netloc:
        user_pw, host_port = netloc.split('@')
        username, password = user_pw.split(':')
        netloc = '%s:***@%s' % (username, host_port)
        parts[1] = netloc
    return urlparse.urlunparse(parts)
