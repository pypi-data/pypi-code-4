
from zope import schema
from zope.interface import Interface

from c2.app.zipdownload import ZipDownloadMessageFactory as _


class IZipDownloadControlPanel(Interface):
    """Zip Download setting interface
    """

    encoding = schema.TextLine(
        required=True,
        title=_(u'Filename encoding'),
        description=_(u'filename_encoding_help',
                      default=u'Filename Encoding in zip'),
        default=u"utf-8",
        )



