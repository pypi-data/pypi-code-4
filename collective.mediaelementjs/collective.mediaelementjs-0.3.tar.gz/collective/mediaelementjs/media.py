from persistent import Persistent

from zope.annotation import factory
from zope.component import adapts
from zope.interface import implements

from collective.mediaelementjs.interfaces import IVideo, IMediaInfo, IAudio


class VideoInfo(Persistent):
    implements(IMediaInfo)
    adapts(IVideo)

    def __init__(self):
        self.height = None
        self.width = None
        self.duration = None

VideoInfoAdapter = factory(VideoInfo)


class AudioInfo(Persistent):
    implements(IMediaInfo)
    adapts(IAudio)

    def __init__(self):
        self.duration = None

AudioInfoAdapter = factory(AudioInfo)
