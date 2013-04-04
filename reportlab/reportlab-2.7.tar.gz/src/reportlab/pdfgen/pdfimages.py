#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/pdfgen/pdfimages.py
__version__=''' $Id$ '''
__doc__="""
Image functionality sliced out of canvas.py for generalization
"""

import os
import string
from types import StringType
import reportlab
from reportlab import rl_config
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase import pdfdoc
from reportlab.lib.utils import fp_str, getStringIO
from reportlab.lib.utils import import_zlib, haveImages
from reportlab.lib.boxstuff import aspectRatioFix


class PDFImage:
    """Wrapper around different "image sources".  You can make images
    from a PIL Image object, a filename (in which case it uses PIL),
    an image we previously cached (optimisation, hardly used these
    days) or a JPEG (which PDF supports natively)."""

    def __init__(self, image, x,y, width=None, height=None, caching=0):
        self.image = image
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.filename = None
        self.imageCaching = caching
        # the following facts need to be determined,
        # whatever the source. Declare what they are
        # here for clarity.
        self.colorSpace = 'DeviceRGB'
        self.bitsPerComponent = 8
        self.filters = []
        self.source = None # JPEG or PIL, set later
        self.getImageData()

    def jpg_imagedata(self):
        #directly process JPEG files
        #open file, needs some error handling!!
        fp = open(self.image, 'rb')
        try:
            result = self._jpg_imagedata(fp)
        finally:
            fp.close()
        return result

    def _jpg_imagedata(self,imageFile):
        info = pdfutils.readJPEGInfo(imageFile)
        self.source = 'JPEG'
        imgwidth, imgheight = info[0], info[1]
        if info[2] == 1:
            colorSpace = 'DeviceGray'
        elif info[2] == 3:
            colorSpace = 'DeviceRGB'
        else: #maybe should generate an error, is this right for CMYK?
            colorSpace = 'DeviceCMYK'
        imageFile.seek(0) #reset file pointer
        imagedata = []
        #imagedata.append('BI /Width %d /Height /BitsPerComponent 8 /ColorSpace /%s /Filter [/Filter [ /ASCII85Decode /DCTDecode] ID' % (info[0], info[1], colorSpace))
        imagedata.append('BI /W %d /H %d /BPC 8 /CS /%s /F [%s/DCT] ID' % (imgwidth, imgheight, colorSpace, rl_config.useA85 and '/A85 ' or ''))
        #write in blocks of (??) 60 characters per line to a list
        data = imageFile.read()
        if rl_config.useA85:
            data = pdfutils._AsciiBase85Encode(data)
        pdfutils._chunker(data,imagedata)
        imagedata.append('EI')
        return (imagedata, imgwidth, imgheight)

    def cache_imagedata(self):
        image = self.image
        if not pdfutils.cachedImageExists(image):
            zlib = import_zlib()
            if not zlib: return
            if not haveImages: return
            pdfutils.cacheImageFile(image)

        #now we have one cached, slurp it in
        cachedname = os.path.splitext(image)[0] + (rl_config.useA85 and '.a85' or '.bin')
        imagedata = open(cachedname,'rb').readlines()
        #trim off newlines...
        imagedata = map(string.strip, imagedata)
        return imagedata

    def PIL_imagedata(self):
        image = self.image
        if image.format=='JPEG':
            fp=image.fp
            fp.seek(0)
            return self._jpg_imagedata(fp)
        self.source = 'PIL'
        zlib = import_zlib()
        if not zlib: return

        # Use the colorSpace in the image
        if image.mode == 'CMYK':
            myimage = image
            colorSpace = 'DeviceCMYK'
            bpp = 4
        else:
            myimage = image.convert('RGB')
            colorSpace = 'RGB'
            bpp = 3
        imgwidth, imgheight = myimage.size

        # this describes what is in the image itself
        # *NB* according to the spec you can only use the short form in inline images
        imagedata=['BI /W %d /H %d /BPC 8 /CS /%s /F [%s/Fl] ID' % (imgwidth, imgheight,colorSpace, rl_config.useA85 and '/A85 ' or '')]

        #use a flate filter and, optionally, Ascii Base 85 to compress
        raw = myimage.tostring()
        assert len(raw) == imgwidth*imgheight*bpp, "Wrong amount of data for image"
        data = zlib.compress(raw)    #this bit is very fast...
        if rl_config.useA85:
            data = pdfutils._AsciiBase85Encode(data) #...sadly this may not be
        #append in blocks of 60 characters
        pdfutils._chunker(data,imagedata)
        imagedata.append('EI')
        return (imagedata, imgwidth, imgheight)

    def non_jpg_imagedata(self,image):
        if not self.imageCaching:
            imagedata = pdfutils.cacheImageFile(image,returnInMemory=1)
        else:
            imagedata = self.cache_imagedata()
        words = string.split(imagedata[1])
        imgwidth = string.atoi(words[1])
        imgheight = string.atoi(words[3])
        return imagedata, imgwidth, imgheight

    def getImageData(self,preserveAspectRatio=False):
        "Gets data, height, width - whatever type of image"
        image = self.image

        if type(image) == StringType:
            self.filename = image
            if os.path.splitext(image)[1] in ['.jpg', '.JPG', '.jpeg', '.JPEG']:
                try:
                    imagedata, imgwidth, imgheight = self.jpg_imagedata()
                except:
                    imagedata, imgwidth, imgheight = self.non_jpg_imagedata(image)  #try for normal kind of image
            else:
                imagedata, imgwidth, imgheight = self.non_jpg_imagedata(image)
        else:
            import sys
            if sys.platform[0:4] == 'java':
                #jython, PIL not available
                imagedata, imgwidth, imgheight = self.JAVA_imagedata()
            else:
                imagedata, imgwidth, imgheight = self.PIL_imagedata()
        self.imageData = imagedata
        self.imgwidth = imgwidth
        self.imgheight = imgheight
        self.width = self.width or imgwidth
        self.height = self.height or imgheight

    def drawInlineImage(self, canvas, preserveAspectRatio=False,anchor='sw'):
        """Draw an Image into the specified rectangle.  If width and
        height are omitted, they are calculated from the image size.
        Also allow file names as well as images.  This allows a
        caching mechanism"""
        width = self.width
        height = self.height
        if width<1e-6 or height<1e-6: return False
        x,y,self.width,self.height, scaled = aspectRatioFix(preserveAspectRatio,anchor,self.x,self.y,width,height,self.imgwidth,self.imgheight)
        # this says where and how big to draw it
        if not canvas.bottomup: y = y+height
        canvas._code.append('q %s 0 0 %s cm' % (fp_str(self.width), fp_str(self.height, x, y)))
        # self._code.extend(imagedata) if >=python-1.5.2
        for line in self.imageData:
            canvas._code.append(line)
        canvas._code.append('Q')
        return True

    def format(self, document):
        """Allow it to be used within pdfdoc framework.  This only
        defines how it is stored, not how it is drawn later."""

        dict = pdfdoc.PDFDictionary()
        dict['Type'] = '/XObject'
        dict['Subtype'] = '/Image'
        dict['Width'] = self.width
        dict['Height'] = self.height
        dict['BitsPerComponent'] = 8
        dict['ColorSpace'] = pdfdoc.PDFName(self.colorSpace)
        content = string.join(self.imageData[3:-1], '\n') + '\n'
        strm = pdfdoc.PDFStream(dictionary=dict, content=content)
        return strm.format(document)

if __name__=='__main__':
    srcfile = os.path.join(
                os.path.dirname(reportlab.__file__),
                'test',
                'pythonpowered.gif'
                )
    assert os.path.isfile(srcfile), 'image not found'
    pdfdoc.LongFormat = 1
    img = PDFImage(srcfile, 100, 100)
    import pprint
    doc = pdfdoc.PDFDocument()
    print 'source=',img.source
    print img.format(doc)
