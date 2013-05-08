import time
import urllib2
from functools import wraps
import StringIO
import random
from wm.sampledata import logger
# see
# http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
# http://stackoverflow.com/questions/9446387/how-to-retry-urllib2-request-when-failed

def _retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck, e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print msg
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry


@_retry(urllib2.URLError, tries=5, delay=2, logger=logger)
def _download(url):
    """try to download the url 5 times, with exponential delay.
    first delay 2 seconds, second 4, third 8, etc
    """
    logger.info('Downloading %s' % url)
    return urllib2.urlopen(url)
    
    
    
#http://lorempixel.com/
CATEGORIES = ['abstract','animals','business','cats','city','food','nightlife',
              'fashion','people','nature','sports','technics','transport',]

    
def _getImage(width=1024, height=768, category=None, gray=False, index=None, text=None):
    """obtains an image from lorempixel.com
    
    for possible categories see ``CATEGORIES``
    """
    
    url = 'http://lorempixel.com/'
    params = []
    
    if gray:
        params.append('g/')
    params.append('%d/%d/' % (width, height))
    if category:
        params.append(category + '/')
        if index:
            params.append('%d/' % index)    
    if text:
        params.append('%s/' % text)

    url = url + ''.join(params)
    
    info = _download(url)
    data = info.read() 
    return StringIO.StringIO(data)


RATIOS = [(16,9), (4,3)]

def _getRandomImage(long_edge=1024, category=None, gray=None):
    """returns a random image from lorempixel.com (portrait or landscape) in one of the available
    RATIOS
    
    set gray to True to force grayscale pictures and to False to force color 
    pictures
    """
    ratio = random.choice(RATIOS)
    ratio = float(ratio[0])/ratio[1]
    landscape = random.choice([True, False])
    if gray is None:
        gray = random.choice([True, False])
        
    if landscape:
        width = long_edge
        height = int(long_edge / ratio)
    else:
        height = long_edge
        width = int(long_edge / ratio)

    return _getImage(width, height, category=category, gray=gray)
