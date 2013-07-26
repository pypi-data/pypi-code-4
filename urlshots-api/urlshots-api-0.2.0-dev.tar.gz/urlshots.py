"""
"""
import logging

import urllib3
import pyconfig
from pytool.lang import hashed_singleton, Namespace, UNSET


__version__ = '0.2.0-dev'


@hashed_singleton
class API(object):
    """
    This is the UrlShots API client.

    :param api_key: API key for use with URLshots API (optional)
    :param host: URLshots API hostname (default: ``'urlshots.net'``)
    :param timeout: Timeout for requests to the API (default: ``20``)
    :param delay: Delay in seconds after loading before screenshotting
                  (default: ``0``)
    :param jpeg: JPEG compression; 0 means no JPEG, return a PNG instead
                 (default: ``75``)
    :param compress: Whether to compress a PNG to an 8-bit indexed image
                     (default: ``0``)
    :param actions: Actions chain as a string (default: ``None``)
    :param concurrency: Maximum connection pool size for use in
                        multithreaded or concurrent applications (default:
                        ``1``)
    :param window: Size of the capture window to use as a tuple of ``(width,
                   height)`` (default: ``(1260, 840)``)
    :param script: A Javascript snippet to execute after page load (optional)
    :type host: str
    :type timeout: int
    :type delay: int
    :type jpeg: int
    :type compress: int
    :type actions: str
    :type concurrency: int
    :type window: tuple
    :type script: str

    .. method:: image

       Return a binary image of a screenshot of `url`. The returned image is
       suitable for directly writing to a filesystem, or opening in an image
       library such as PIL.

       If the URLshots API returns a non-200 HTTP status, indicating it was
       unable to capture a shot, then ``None`` will be returned.

       :param url: A URL to capture
       :type url: str

    """
    opts = Namespace()
    # Client options
    opts.host = 'urlshots.net'
    opts.concurrency = 1
    opts.timeout = 20
    # API options
    opts.api_key = UNSET
    opts.delay = 0
    opts.jpeg = 75
    opts.compress = 0
    opts.actions = UNSET
    opts.window = (1260, 840)
    opts.script = UNSET
    # This converts the opts to pyconfig settings
    for name, value in opts:
        setattr(opts, name, pyconfig.setting('urlshots.' + name, value))
    del name, value # Remove left over vars so they don't end up in the class

    def __init__(self, **kwargs):
        # Parse keyword options
        for name, value in self.opts:
            if name in kwargs:
                setattr(self.opts, name, kwargs.pop(name))
        # This is our thread safe connection pool, thanks urllib3!
        self.http = urllib3.HTTPConnectionPool(self.opts.host,
                timeout=self.opts.timeout, maxsize=self.opts.concurrency)
        self.log = logging.getLogger('urlshots')
        # Debug the options in case folks want to know
        self.log.debug("Options:")
        for name, value in self.opts:
            self.log.debug("  %s = %r", name, value)

    def _params(self):
        """ Return the instance options as a set of params for the API. """
        params = self.opts.as_dict()
        # Remove the options that are not for the API
        for name in 'concurrency', 'timeout', 'host':
            params.pop(name)
        # Remove actions and script if they're not set
        for name in 'actions', 'script', 'api_key':
            if params[name] is UNSET:
                params.pop(name)
        # Coerce window size
        params['window'] = '{:d}x{:d}'.format(*params['window'])
        return params

    def request(self, url, params=None):
        """ Return a response object for `url`.

            :param str url: URL to capture
            :param dict params: Override parameters sent to API (optional)

        """
        # Get arguments to the API
        params = params or self._params()
        params['url'] = url
        # Make the request
        return self.http.request('GET', '/render', params)

    def image(self, url):
        """ Return a binary image of `url`.

            :param str url: URL to capture

        """
        response = self.request(url)
        if response.status != 200:
            return None
        return response.data

