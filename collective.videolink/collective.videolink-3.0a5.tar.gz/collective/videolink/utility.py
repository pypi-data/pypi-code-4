from zope.annotation.interfaces import IAnnotations
import urllib2
from urllib2 import HTTPError

def add_thumbnail(context, event):
    """
    @param context: Zope object for which the event was fired for. Usually this is Plone content object.

    @param event: Subclass of event.
    """
    if '/portal_factory/' in context.absolute_url():
        return
    annotations = IAnnotations(context)
    try:
        data = annotations['collective.videolink.data']
    except KeyError:
        data = annotations['collective.videolink.data'] = {}
    if data.has_key('thumbnail'):
         return data['thumbnail']

    url = context.getRemoteUrl()

    # if this is a vimeo url
    if url.startswith('http://vimeo.com/') or url.startswith('http://www.vimeo.com/'):
        annotations['collective.videolink.data'] = {}
        videoid = url.split('/')[-1] #vimeo videos are queried by their ids
        req = urllib2.Request("http://vimeo.com/api/v2/video/%s.json" % videoid ,None,{'user-agent':'plone.vimeo/embed'})
        opener = urllib2.build_opener()
        file = opener.open(req)
        metadata = eval(file.read())
        #vimeo wraps their json in a list (square brackets)
        thumbnail_url = metadata[0]['thumbnail_medium'].replace('\\','')
        annotations['collective.videolink.data']['thumbnail'] = data['thumbnail'] = thumbnail_url
        
        return thumbnail_url

    #if this is a viddler url
    if url.startswith('http://viddler.com/') or url.startswith('http://www.viddler.com/'):
        annotations['collective.videolink.data'] = {}
        req = urllib2.Request("http://lab.viddler.com/services/oembed/?url=%s/&type=simple&format=json" % url, None,{'user-agent':'plone.viddler/embed'})
        opener = urllib2.build_opener()
        file = opener.open(req)
        metadata = eval(file.read())
        print metadata
        try:
            thumbnail_url = metadata['thumbnail_url'].replace('\\','')
        except KeyError:
            thumbnail_url = ''
        data['thumbnail'] = thumbnail_url
        annotations['collective.videolink.data']['thumbnail'] = data['thumbnail'] = thumbnail_url
        return thumbnail_url

    #if this is a youtube url
    if url.startswith('http://youtube.com/') or url.startswith('http://www.youtube.com/'):
        annotations['collective.videolink.data'] = {}
        req = urllib2.Request("http://www.youtube.com/oembed?url=%s&format=json" % url, None,{'user-agent':'plone.youtube/embed'})
        opener = urllib2.build_opener()
        file = opener.open(req)
        metadata = eval(file.read())
        thumbnail_url = metadata['thumbnail_url'].replace('\\','')
        data['thumbnail'] = thumbnail_url
        annotations['collective.videolink.data']['thumbnail'] = data['thumbnail'] = thumbnail_url
        return thumbnail_url

    if len(url) > 10:
        req = urllib2.Request("http://oohembed.com/oohembed/?url=%s" % url, None, {'user-agent':'plone.collective.video/embed'})
        opener = urllib2.build_opener()
        try:
            file = opener.open(req)
        except HTTPError:
            return
        metadata = eval(file.read())
        thumbnail_url = metadata['thumbnail_url'].replace('\\','')
        data['thumbnail'] = thumbnail_url
        annotations['collective.videolink.data']['thumbnail'] = data['thumbnail'] = thumbnail_url
        return thumbnail_url
