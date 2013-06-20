
from zope.component.interfaces import ObjectEvent
from zope.interface import implements


from c2.app.zipdownload.interfaces import IFileDownloadEvent

class FileDownloadEvent(ObjectEvent):
    """

    """
    implements(IFileDownloadEvent)
