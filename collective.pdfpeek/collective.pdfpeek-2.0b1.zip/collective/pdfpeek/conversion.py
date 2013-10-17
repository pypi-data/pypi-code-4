# -*- coding: utf-8 -*-
from BTrees.OOBTree import OOBTree
from OFS.Image import Image as OFSImage
from PIL import Image
from PyPDF2 import PdfFileReader
from PyPDF2.utils import PdfReadError

from cStringIO import StringIO
from collective.pdfpeek.interfaces import IPDFDataExtractor
from collective.pdfpeek.interfaces import IPDF
from collective.pdfpeek.interfaces import IPDFPeekConfiguration
from plone.registry.interfaces import IRegistry
from zope.annotation.interfaces import IAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
from zope.interface import implementer

import logging
import subprocess

logger = logging.getLogger('collective.pdfpeek.conversion')

inch = 72.0
cm = inch / 2.54
mm = cm * 0.1


@implementer(IPDFDataExtractor)
class AbstractPDFExtractor(object):
    """Convert PDF in plone.app.contenttypes files
    """

    img_thumb_format = "PNG"
    img_thumb_quality = 60
    img_thumb_optimize = True
    img_thumb_progressive = False

    img_preview_format = "PNG"
    img_preview_quality = 90
    img_preview_optimize = True
    img_preview_progressive = False

    def __init__(self, context):
        self.context = context

    @property
    def errmsg(self):
        return "Failed to convert PDF to images with PDFPeek on {context.id}."\
            .format(context=self.context)

    @property
    def successmsg(self):
        return "Converted PDF to images with PDFPeek on {context.id}."\
            .format(context=self.context)

    @property
    def content_type(self):
        raise NotImplementedError

    @property
    def data(self):
        raise NotImplementedError

    def _fixPdf(self, string):
        try:
            result = string + "\n%%EOF\n"
            return result
        except Exception:
            logger.error("Unable to fix pdf file.")
            return string

    @property
    def pdf(self):
        pdf = None
        try:
            pdf = PdfFileReader(StringIO(self.data))
        except:
            logger.warn("Error opening pdf file, trying to fix it...")
            fixed_data = self._fixPdf(self.data)

            # try to reopen the pdf file again
            try:
                pdf = PdfFileReader(StringIO(fixed_data))
            except:
                logger.warn("This pdf file cannot be fixed.")

        if pdf and pdf.isEncrypted:
            try:
                decrypt = pdf.decrypt('')
                if decrypt == 0:
                    logger.warn("This pdf is password protected.")
            except:
                logger.warn("Errors while decrypting the pdf file.")

        if pdf is None:
            remove_image_previews(self.context)

        return pdf

    @property
    def pages(self):
        if self.pdf:
            if self.settings.page_limit <= 0:
                return self.pdf.getNumPages()

            return min(self.pdf.getNumPages(), self.settings.page_limit)

        return 0

    @property
    def metadata(self):
        data = {}
        if self.pdf:
            try:
                data = dict(self.pdf.getDocumentInfo())
            except (TypeError, PdfReadError) as e:
                logger.error("{0}: {1}".format(e.__class__, e))

            data['width'] = float(self.pdf.getPage(0).mediaBox.getWidth())
            data['height'] = float(self.pdf.getPage(0).mediaBox.getHeight())
            data['pages'] = self.pdf.getNumPages()

        return data

    @property
    def settings(self):
        registry = getUtility(IRegistry)
        return registry.forInterface(IPDFPeekConfiguration)

    def get_thumbnails(self, page_start=0, pages=1):
        thumb_size = (self.settings.thumbnail_width,
                      self.settings.thumbnail_length)
        preview_size = (self.settings.preview_width,
                        self.settings.preview_length)

        # set up the images dict
        images = {}

        # Extracting self.pages pages
        logger.info("Extracting {0:d} page screenshots".format(self.pages))

        for page in range(page_start, page_start + pages):
            # for each page in the pdf file,
            # set up a human readable page number counter starting at 1
            page_number = page + 1
            # set up the image object ids and titles
            image_id = "%d_preview" % page_number
            image_title = "Page %d Preview" % page_number
            image_thumb_id = "%d_thumb" % page_number
            image_thumb_title = "Page %d Thumbnail" % page_number
            # create a file object to store the thumbnail and preview in
            raw_image_thumb = StringIO()
            raw_image_preview = StringIO()
            # run ghostscript, convert pdf page into image
            raw_image = self.ghostscript_transform(page_number)
            # use PIL to generate thumbnail from image_result
            try:
                img_thumb = Image.open(StringIO(raw_image))
            except IOError:
                logger.error("This is not an image: {0}".format(raw_image))
                break

            img_thumb.thumbnail(thumb_size, Image.ANTIALIAS)
            # save the resulting thumbnail in the file object
            img_thumb.save(raw_image_thumb,
                           format=self.img_thumb_format,
                           quality=self.img_thumb_quality,
                           optimize=self.img_thumb_optimize,
                           progressive=self.img_thumb_progressive)
            # use PIL to generate preview from image_result
            img_preview = Image.open(StringIO(raw_image))
            img_preview.thumbnail(preview_size, Image.ANTIALIAS)
            # save the resulting thumbnail in the file object
            img_preview.save(raw_image_preview,
                             format=self.img_preview_format,
                             quality=self.img_preview_quality,
                             optimize=self.img_preview_optimize,
                             progressive=self.img_preview_progressive)
            # create the OFS.Image objects
            image_full_object = OFSImage(
                image_id, image_title, raw_image_preview)
            image_thumb_object = OFSImage(
                image_thumb_id, image_thumb_title, raw_image_thumb)
            # add the objects to the images dict
            images[image_id] = image_full_object
            images[image_thumb_id] = image_thumb_object
            logger.info("Thumbnail generated.")

        return images

    def ghostscript_transform(self, page_num):
        """
        ghostscript_transform takes an AT based object with an IPDF interface
        and a page number argument and converts that page number of the pdf
        file to a png image file.
        """
        first_page = "-dFirstPage={0:d}".format(page_num)
        last_page = "-dLastPage={0:d}".format(page_num)
        gs_cmd = [
            "gs",
            "-q",
            "-dSAFER",
            "-dBATCH",
            "-dNOPAUSE",
            "-sDEVICE=png16m",
            "-dGraphicsAlphaBits=4",
            "-dTextAlphaBits=4",
            first_page,
            last_page,
            "-r59x56",
            "-sOutputFile=%stdout",
            "-",
        ]

        image_result = None
        """run the ghostscript command on the pdf file,
        capture the output png file of the specified page number"""
        bufsize = -1
        gs_process = subprocess.Popen(gs_cmd,
                                      bufsize=bufsize,
                                      stdout=subprocess.PIPE,
                                      stdin=subprocess.PIPE)
        gs_process.stdin.write(self.data)
        image_result = gs_process.communicate()[0]
        gs_process.stdin.close()
        return_code = gs_process.returncode
        if return_code == 0:
            logger.info("Ghostscript processed one page of a pdf file.")
        else:
            logger.warn("Ghostscript process did not exit cleanly! "
                        "Error Code: {0}".format(return_code))
            image_result = None
        return image_result

    def __call__(self):
        if self.pdf:
            alsoProvides(self.context, IPDF)
            alsoProvides(self.context, IAttributeAnnotatable)

            # Use BTrees
            storage = OOBTree()
            storage['image_thumbnails'] = self.get_thumbnails(0, self.pages)

            annotations = IAnnotations(self.context)
            annotations['pdfpeek'] = storage

            self.context.reindexObject()
            logger.info(self.successmsg)
            return self.successmsg
        else:
            logger.info(self.errormsg)
            return self.errmsg


def remove_image_previews(content):
    """
    This function removes the image preview annotations if a pdf file is
    removed
    """
    # a file was uploaded that is not a PDF
    # remove the pdf file
    content.filepreview = None
    # remove the marker interface
    noLongerProvides(content, IPDF)

    # remove the annotated images
    annotations = IAnnotations(content)
    if 'pdfpeek' in annotations:
        del annotations['pdfpeek']
    content.reindexObject()
    msg = "Removed preview annotations from %s." % content.id
    logger.info(msg)
    return msg
