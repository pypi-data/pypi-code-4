import urllib
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
def viddler_check(url):
    """Check to see if the given url is viddler style

      >>> viddler_check('http://someplace.com')
      False
      >>> viddler_check('http://viddler.com/file/somefile.flv')
      False
      >>> viddler_check('http://viddler.com/explore/user/34')
      True
      >>> viddler_check('http://www.viddler.com/explore/viddler/videos/20/')
      True

    """

    host, path, query, fragment = break_url(url)
    if host == 'viddler.com' or host.endswith('.viddler.com'):
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

viddler_check.index = 1000


def _oembed_url(url):
    """Return Oembed url for the video url.

      >>> _oembed_url('http://someplace.com')
      'http://lab.viddler.com/services/oembed/?url=http://someplace.com?skin=rss&type=simple&format=json'

    """

    host, path, query, fragment = break_url(url)
    file_url = url
    return "http://lab.viddler.com/services/oembed/?url=%s/&&type=simple&format=json" % file_url

@adapter(str, int)
@implementer(IEmbedCode)
def viddler_generator(url, width):
    """ A quick check for the right url

    >>> html = viddler_generator('http://viddler.com/explorer/user/4',
    ...                         width=400)
    >>> 'showplayer.swf?file=http%3A//blip.tv/file/get/random.flv' in html
    True

    """
    host, path, query, fragment = break_url(url)

    oembed = remote_content(_oembed_url(url))
    oembed = eval(oembed)

    return oembed['html'].replace('\\','')

def _populate_viddler_data(oembed, metadata):
    """Use oembed information to pull out the metadata information.

      >>> oembed = '''{"version":"1.0",
      ... "type":"video",
      ... "width":437,
      ... "height":348,
      ... "title":"Poultry Farmer",
      ... "url":"http:\/\/www.viddler.com\/explore\/wroc\/videos\/4\/",
      ... "thumbnail_url":"http:\/\/cdn-thumbs.viddler.com\/thumbnail_2_ae7262b3.jpg",
      ... "author_name":"wroc",
      ... "author_url":"http:\/\/www.viddler.com\/explore\/wroc\/",
      ... "provider":"Viddler",
      ... "provider_url":"http:\/\/www.viddler.com\/",
      ... "html":"<object classid=\"clsid:D27CDB6E-AE6D-11cf-96B8-444553540000\" width=\"437\" height=\"348\" id=\"viddlerplayer-ae7262b3\"><param name=\"movie\" value=\"http:\/\/www.viddler.com\/simple\/ae7262b3\/\" \/><param name=\"allowScriptAccess\" value=\"always\" \/><param name=\"wmode\" value=\"transparent\" \/><param name=\"allowFullScreen\" value=\"true\" \/><embed src=\"http:\/\/www.viddler.com\/simple\/ae7262b3\/\" width=\"437\" height=\"348\" type=\"application\/x-shockwave-flash\" wmode=\"transparent\" allowScriptAccess=\"always\" allowFullScreen=\"true\" name=\"viddlerplayer-ae7262b3\" ><\/embed><\/object>"}<?xml version="1.0" ?>
      ... '''

      >>> metadata = VideoMetadata()
      >>> _populate_viddler_data(oembed, metadata)

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
def viddler_metadata_lookup(url):
    """Retrieve metadata information regarding a viddler video url."""

    data = VideoMetadata()
    oembed = remote_content(_oembed_url(url))
    _populate_viddler_data(oembed, data)

    return data
