# -*- coding: utf-8 -*-
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import implements

from Products.CMFCore.utils import getToolByName

from redturtle.video.interfaces import IVideoEmbedCode

from redturtle.video.browser.videoembedcode import VideoEmbedCode
from collective.rtvideo.mediacore.config import DEFAULT_TIMEOUT, logger

import urllib2
import cjson
import urlparse
from urllib import urlencode


class IMediaCoreEmbedCode(IVideoEmbedCode):
    """
    @summary: Imarker interface for mediacore embedding
    @author: lucabel
    """


class JWPlayerEmbedCode(VideoEmbedCode):
    """ MediaCoreEmbedCode
    Integration with mediacore system, forcing jwplayer
    Implement your own class to provide meta-information to
    play video.

    >>> from zope.component import getMultiAdapter
    >>> from redturtle.video.interfaces import IVideoEmbedCode
    >>> from collective.rtvideo.mediacore.tests.base import TestRequest
    >>> from collective.rtvideo.mediacore.tests.dummies import DummyVideo
    >>> from collective.rtvideo.mediacore.videoembedcode import JWPlayerEmbedCode
    >>> request = TestRequest()
    >>> dummyvideo = DummyVideo()
    >>> adapter = JWPlayerEmbedCode(dummyvideo, request)
    >>> adapter.get_mediacore_base_url()
    'http://example.com'
    >>> adapter.get_mediacore_uid_url()
    'http://example.com/mediainfo/media_unique_id?slug=example&timeout=15'
    >>> adapter.get_mediacore_file_url('uid')
    'http://example.com/files/uid'
    """
    implements(IMediaCoreEmbedCode)
    template = ViewPageTemplateFile('jwplayer_template.pt')

    def get_mediacore_base_url(self):
        '''
        The url to retrieve the uid of the mediacore video
        '''
        remoteurl = self.context.getRemoteUrl()
        parsed_url = urlparse.urlparse(remoteurl)
        return '%s://%s' % (parsed_url.scheme, parsed_url.netloc)

    def get_mediacore_uid_url(self):
        '''
        The url to retrieve the uid of the mediacore video
        '''
        mediacore_url = self.get_mediacore_base_url()
        remoteurl = self.context.getRemoteUrl()
        media_slug = remoteurl.split('/')[-1]
        params = {'slug': media_slug,
                  'timeout': DEFAULT_TIMEOUT}
        qs = urlencode(params)
        return '%s/mediainfo/media_unique_id?%s' % (mediacore_url, qs)

    def get_mediacore_file_url(self, unique_id):
        '''
        The url to retrieve the url to get the file from mediacore
        '''
        mediacore_url = self.get_mediacore_base_url()
        return '%s/files/%s' % (mediacore_url, unique_id)

    def get_media_metadata(self):
        """
        @author: lucabel
        @description: provide media metadata
        """
        mediacore_uid_url = self.get_mediacore_uid_url()
        try:
            data = urllib2.urlopen(mediacore_uid_url).read()
        except:
            msg = 'Problem retrieving %s' % mediacore_uid_url
            logger.exception(msg)
            return
        data = cjson.decode(data)
        data['file_remoteurl'] = self.get_mediacore_file_url(data['unique_id'])
        return data

    def get_variables(self):
        """
        @author: lucabel
        @summary: We need to write in the template some js variable
        useful for jwplayer. If no meta available (e.g. mediacore is
        not responding, return nothing)
        Extend this class to provide a get_media_metadata to provide
        information
        """
        meta = self.get_media_metadata()
        if meta:
            meta['width'] = self.getWidth()
            meta['height'] = self.getHeight()
            VARIABLES = """
            var jwplayer_file = '%(file_remoteurl)s';
            var jwplayer_image = '%(image_url)s';
            var jwplayer_h = '%(height)spx';
            var jwplayer_w = '%(width)spx';
            """
            return VARIABLES % meta

    def check_is_portal_factory(self):
        portal_factory = getToolByName(self.context, 'portal_factory', None)
        if portal_factory is not None:
            return portal_factory.isTemporary(self.context)
        else:
            return False
