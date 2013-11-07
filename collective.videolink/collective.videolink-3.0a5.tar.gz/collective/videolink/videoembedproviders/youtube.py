import urllib2
try:
    import json
except ImportError:
    import simplejson as json
from xml.dom import minidom
from xml.parsers import expat
from urlparse import urlunsplit
from p4a.videoembed.utils import remote_content, break_url, xpath_text
from p4a.videoembed.interfaces import provider
from p4a.videoembed.interfaces import IEmbedCode
from p4a.videoembed.interfaces import IMediaURL
from p4a.videoembed.interfaces import IURLChecker
from p4a.videoembed.interfaces import IVideoMetadataLookup
from p4a.videoembed.interfaces import VideoMetadata
from zope.component import adapts, adapter, queryUtility
from zope.interface import implements, implementer, Interface
from zope.schema import TextLine

import logging
logger = logging.getLogger('p4a.videoembed.providers.youtube')

class IYoutubeConfig(Interface):
    """Configuration for accessing the RESTful api for youtube."""

    dev_id = TextLine(title=u'Developer Id',
                      required=True)

# YouTube!
@provider(IURLChecker)
def youtube_check(url):
    host, path, query, fragment = break_url(url)
    if host.endswith('youtube.com') and query.has_key('v'):
        return True
    return False

youtube_check.index = 100

# This is the appropriate way of getting the thumbnail image.  Due to not
# wanting to add the dev_id requirement, this code will not be used yet
def _populate_youtube_data(oembed,metadata):

    oembed = eval(oembed)

    # remove icky backslashes as we store the metadata
    metadata.thumbnail_url = oembed['thumbnail_url'].replace('\\','')
    metadata.title = oembed['title'].replace('\\','')
    metadata.author = oembed['author_name'].replace('\\','')
@adapter(str)
@implementer(IVideoMetadataLookup)
def youtube_metadata_lookup(url):
    """Retrieve metadata information regarding a youtube video url."""

    data = VideoMetadata()
    oembed = remote_content(_oembed_url(url))
    _populate_youtube_data(oembed, data)


def _oembed_url(url):
    """Return Oembed url for the video url.

      >>> _oembed_url('http://someplace.com')
      'http://www.youtube.com/oembed?url=http%3A//someplace.com&format=json'

    """

    host, path, query, fragment = break_url(url)
    file_url = url
    return "http://www.youtube.com/oembed?url=%s&format=json" % file_url


@adapter(str, int)
@implementer(IEmbedCode)
def youtube_generator(url, width):
    """ A quick check for the right url

    >>> print youtube_generator('http://www.youtube.com/watch?v=1111',
    ...                         width=400)
    <object width="400" height="330"><param name="movie" value="http://www.youtube.com/v/1111"></param><param name="wmode" value="transparent"></param><embed src="http://www.youtube.com/v/1111" type="application/x-shockwave-flash" wmode="transparent" width="400" height="330"></embed></object>

    """
    host, path, query, fragment = break_url(url)

    oembed = remote_content(_oembed_url(url))
    oembed = json.loads(oembed)
    return oembed['html']

class youtube_mediaurl(object):
    """Returns the quicktime media url for a piece of youtube content:

           >>> url = youtube_mediaurl('http://www.youtube.com/watch?v=1111')
           >>> url.media_url
           'http://youtube.com/v/1111.swf'
           >>> url.mimetype
           'application/x-shockwave-flash'
    """
    implements(IMediaURL)
    adapts(str)
    def __init__(self, url):
        host, path, query, fragment = break_url(url)
        video_id = query['v']
        self.mimetype = 'application/x-shockwave-flash'
        self.media_url = 'http://youtube.com/v/%s.swf'%video_id
