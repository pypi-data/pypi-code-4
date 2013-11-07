import urllib
try:
    import json
except ImportError:
    import simplejson as json
from xml.dom import minidom
from p4a.videoembed.utils import (break_url, xpath_text,
                                  xpath_attr, squeeze_xml,
                                  remote_content)
from p4a.videoembed.interfaces import provider
from p4a.videoembed.interfaces import IEmbedCode
from p4a.videoembed.interfaces import IURLChecker
from p4a.videoembed.interfaces import IVideoMetadataLookup
from p4a.videoembed.interfaces import VideoMetadata
from zope.interface import implementer
from zope.component import adapter

@provider(IURLChecker)
def bliptv_check(url):
    """Check to see if the given url is bliptv style

      >>> bliptv_check('http://someplace.com')
      False
      >>> bliptv_check('http://bliptv.com/file/somefile.flv')
      False
      >>> bliptv_check('http://bliptv.com/explore/user/34')
      True
      >>> bliptv_check('http://www.bliptv.com/explore/bliptv/videos/20/')
      True

    """

    host, path, query, fragment = break_url(url)
    if host == 'blip.tv' or host.endswith('.blip.tv'):
        return True
        pieces = [x for x in path.split('/') if x]
        if len(pieces) == 3 \
               and pieces[0] == 'explore' \
               and pieces[2].isdigit():
            return True
        if len(pieces) == 4 \
               and pieces[0] == 'explore' \
               and pieces[3].isdigit():
            return True
    return False

bliptv_check.index = 1000


def _oembed_url(url):
    """Return Oembed url for the video url.

      >>> _oembed_url('http://someplace.com')
      'http://lab.bliptv.com/services/oembed/?url=http://someplace.com?skin=rss&type=simple&format=json'

    """

    host, path, query, fragment = break_url(url)
    file_url = url
    return "http://www.oohembed.com/oohembed/?url=%s" % file_url

@adapter(str, int)
@implementer(IEmbedCode)
def bliptv_generator(url, width):
    """ A quick check for the right url

    >>> html = bliptv_generator('http://bliptv.com/explorer/user/4',
    ...                         width=400)
    >>> 'showplayer.swf?file=http%3A//blip.tv/file/get/random.flv' in html
    True

    """
    oembed = remote_content(_oembed_url(url))
    oembed = json.loads(oembed)

    return oembed['html']

def _populate_bliptv_data(oembed, metadata):
    """Use oembed information to pull out the metadata information.

      >>> oembed = '''{"version":"1.0",
      ... "type":"video",
      ... "width":437,
      ... "height":348,
      ... "title":"Poultry Farmer",
      ... "url":"http:\/\/www.bliptv.com\/explore\/wroc\/videos\/4\/",
      ... "thumbnail_url":"http:\/\/cdn-thumbs.bliptv.com\/thumbnail_2_ae7262b3.jpg",
      ... "author_name":"wroc",
      ... "author_url":"http:\/\/www.bliptv.com\/explore\/wroc\/",
      ... "provider":"Viddler",
      ... "provider_url":"http:\/\/www.bliptv.com\/",
      ... "html":"<object classid=\"clsid:D27CDB6E-AE6D-11cf-96B8-444553540000\" width=\"437\" height=\"348\" id=\"bliptvplayer-ae7262b3\"><param name=\"movie\" value=\"http:\/\/www.bliptv.com\/simple\/ae7262b3\/\" \/><param name=\"allowScriptAccess\" value=\"always\" \/><param name=\"wmode\" value=\"transparent\" \/><param name=\"allowFullScreen\" value=\"true\" \/><embed src=\"http:\/\/www.bliptv.com\/simple\/ae7262b3\/\" width=\"437\" height=\"348\" type=\"application\/x-shockwave-flash\" wmode=\"transparent\" allowScriptAccess=\"always\" allowFullScreen=\"true\" name=\"bliptvplayer-ae7262b3\" ><\/embed><\/object>"}<?xml version="1.0" ?>
      ... '''

      >>> metadata = VideoMetadata()
      >>> _populate_bliptv_data(oembed, metadata)

      >>> metadata.title
      u'Random Video'
      >>> metadata.description
      u'This is a random description.'
      >>> metadata.tags
      set([u'abc', u'def'])
      >>> metadata.thumbnail_url
      u'http://someurl.com/somefile.jpg'
      >>> metadata.author
      u'someuser'

    """
    oembed = eval(oembed)

    # remove icky backslashes as we store the metadata
    metadata.thumbnail_url = oembed['thumbnail_url'].replace('\\','')
    metadata.title = oembed['title'].replace('\\','')
    metadata.author = oembed['author_name'].replace('\\','')

@adapter(str)
@implementer(IVideoMetadataLookup)
def bliptv_metadata_lookup(url):
    """Retrieve metadata information regarding a bliptv video url."""

    data = VideoMetadata()
    oembed = remote_content(_oembed_url(url))
    _populate_bliptv_data(oembed, data)

    return data
