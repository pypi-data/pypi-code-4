from pecan_mount._compat import native_to_unicode, unicodestr


def downgrade_wsgi_ux_to_1x(environ):
    """
    Return a new environ dict for WSGI 1.x from the given WSGI u.x
    environ.
    """
    env1x = {}

    url_encoding = environ[native_to_unicode('wsgi.url_encoding')]
    for k, v in list(environ.items()):
        if k in [native_to_unicode('PATH_INFO'),
                 native_to_unicode('SCRIPT_NAME'),
                 native_to_unicode('QUERY_STRING')]:
            v = v.encode(url_encoding)
        elif isinstance(v, unicodestr):
            v = v.encode('ISO-8859-1')
        env1x[k.encode('ISO-8859-1')] = v

    return env1x


def urljoin(*atoms):
    """Return the given path \*atoms, joined into a single URL.

    This will correctly join a SCRIPT_NAME and PATH_INFO into the
    original URL, even if either atom is blank.
    """
    url = "/".join([x for x in atoms if x])
    while "//" in url:
        url = url.replace("//", "/")
    # Special-case the final url of "", and return "/" instead.
    return url or "/"
