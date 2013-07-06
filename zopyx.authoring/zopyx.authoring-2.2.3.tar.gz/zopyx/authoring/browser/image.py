#####################################################################
# zopyx.authoring
# (C) 2011, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

import PIL
import cStringIO
from Products.Five.browser import BrowserView

def _render_details_cachekey(method, self):
    return (self.context.getImage(),)

def getImageValue(img, field_name):
    field = img.getField(field_name)
    if field is None:
        return ''
    return field.get(img)

class Image(BrowserView):
    """ Helper class for images """

    def supplementaryPDFInformation(self):
        img = self.context
        pil_img = PIL.Image.open(cStringIO.StringIO(str(img.getImage().data)))
        return dict(colorspace=pil_img.mode,
                    pdfScale=getImageValue(img, 'pdfScale'),
                    excludeFromEnumeration=getImageValue(img, 'excludeFromImageEnumeration'),
                    linkToFullScale=getImageValue(img, 'linkToFullScale'),
                    displayInline=getImageValue(img, 'displayInline'),
                    captionPosition=getImageValue(img, 'captionPosition'),
                    )
