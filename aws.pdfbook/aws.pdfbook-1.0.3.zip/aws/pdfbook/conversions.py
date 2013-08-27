# -*- coding: utf-8 -*-
# $Id: conversions.py 247280 2011-12-14 10:22:23Z vincentfretin $
"""Conversion utilities"""

import os
import tempfile
import shutil
from StringIO import StringIO
import HTMLParser

from AccessControl import Unauthorized
try:
    from zope.component.hooks import getSite
except ImportError:
    from zope.app.component.hooks import getSite

from DateTime import DateTime

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.FSImage import FSImage
from Products.CMFDefault.interfaces import IImage
from Products.Archetypes.utils import make_uuid
from Products.CMFPlone.utils import getFSVersionTuple

if getFSVersionTuple() >= (4,0):
    from Products.ATContentTypes.interfaces.image import IATImage
else:
    from Products.ATContentTypes.interface.image import IATImage

from aws.pdfbook.interfaces import IPDFOptions
from aws.pdfbook import logger
from aws.pdfbook.config import SITE_CHARSET

CHAR_MAPPING = {
    u"'": u'\u2019', # Apostrophe Windoz
    u'oe': u'\u0153',
    u'OE': u'\u0152',
    u'...': u'\u2026'
    }

def recode(data):
    """Use recode binary to fix encoding problems
    FIXME: Is it always required ?
    """
    htmlbook_options = IPDFOptions(getSite())
    recodeout, recodein = popen2.popen2(
        "%s %s..html-i18n" %
        (htmlbook_options.recode_path, SITE_CHARSET))
    recodein.write(data)
    recodein.close()
    data = recodeout.read()
    recodeout.close()
    return data


class FileSystemInfo(object):
    """Various temporary places required in filesystem for conversions
    """
    def __init__(self, context):
        self.tmp_dir = tempfile.mkdtemp()
        self.html_filename = os.path.join(self.tmp_dir, context.getId() + '.html')
        self.pdf_filename = '%s-%s-%s.pdf' % (
            context.aq_parent.getId(),
            context.getId(),
            DateTime().strftime('%Y_%m_%d-%Hh%M'))
        self.pdf_filepath = os.path.join(self.tmp_dir, self.pdf_filename)
        return

    def __del__(self):
        """Some cleanups"""
        shutil.rmtree(self.tmp_dir)
        return


class RecodeParser(HTMLParser.HTMLParser):

    def __init__(self, fsinfo):
        HTMLParser.HTMLParser.__init__(self)
        self.fsinfo = fsinfo
        self.data = StringIO(u'')
        self.images = []

    def image_feed(self, tag, attrs):
        """Handle image
        """
        for name, value in attrs:
            if name == 'src':
                new_id = make_uuid()
                self.images.append((new_id, value))
                #path = os.path.basename(v)
                break
        else:
            return

        self.data.write(u'<img src="%s" />' % new_id)

    def handle_comment(self, data):
        self.data.write(u'<!-- %s -->' % data)

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            self.image_feed(tag, attrs)
            return
        self.handle_data(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        if tag == 'img':
            self.image_feed(tag, attrs)
            return
        self.data.write(u'<%s />' % (tag,))

    def handle_endtag(self, tag):
        self.data.write(u'</%s>' % tag)

    def handle_data(self, data):
        """Text handling
        recode data from site charset to iso
        @param data:unicode raw text
        """
        self.data.write(data)

    def recode_data(self, data):
        for k, v in CHAR_MAPPING.items():
            data = data.replace(v, k)
        self.feed(data)
        return self.data.getvalue()

    def save_images(self, context):
        """Save images from ZODB to temp directory
        """
        portal = getSite()
        portal_url = portal.absolute_url()
        if not portal_url.endswith('/'):
            portal_url += '/'

        portal_path = '/'.join(portal.getPhysicalPath())

        reference_tool = getToolByName(portal, 'reference_catalog')
        mtool = getToolByName(portal, 'portal_membership')
        for filename, image in self.images:
            size = None

            # Traverse methods mess with unicode
            if type(image) is unicode:
                image = str(image)
            path = image.replace(portal_url, '')
            #filename = os.path.basename(path)

            item = None
            # using uid
            if 'resolveuid' in image:
                # uid is the traversed value coming after "resolveuid/"
                resolveuidpath = image.split('/')
                resolveuid_idx = resolveuidpath.index('resolveuid')
                try:
                    uuid = resolveuidpath[resolveuid_idx + 1]
                except IndexError:
                    logger.error("Failed to get image uid from %s", image)
                    continue

                item = reference_tool.lookupObject(uuid)

                if len(resolveuidpath) >= resolveuid_idx + 2:
                    size = resolveuidpath[resolveuid_idx + 2]

                logger.debug("Get image from uid %s", uuid)

            if not item:
                # relative url
                try:
                    item = context.restrictedTraverse(image)
                    logger.debug("Get image from context")
                except Unauthorized:
                    logger.warning("Unauthorized to get image from context path %s", item)
                except:
                    logger.debug("Failed to get image from context path %s",
                                 image)

            if not item:
                # absolute url
                image_path = '/'.join((portal_path, path))
                try:
                    item = portal.restrictedTraverse(image_path)
                    logger.debug("Get image from portal")
                except Unauthorized:
                    logger.warning("Unauthorized to get from context path %s", image_path)
                except:
                    logger.error("Failed to get image from portal path %s",
                                 image_path)
                    continue

            if not mtool.checkPermission('View', item):
                logger.warning("Unauthorized to get image %s", item)
                continue

            if item and size:
                try:
                    item = item.restrictedTraverse(size)
                except Unauthorized:
                    logger.warning("Unauthorized to get size %s from image %s",
                                 size, image)
                except:
                    logger.error("Failed to get size %s from image %s",
                                 size, image)
                    pass

            # Eek, we should put an adapter for various image providers (overkill ?).
            data = ''
            if IATImage.providedBy(item):
                data = item.getImage()
                data = getattr(item, 'data', data)
            elif isinstance(item, FSImage):
                data = item._readFile(0)
            elif IImage.providedBy(item) \
                or hasattr(item, 'data'):
                data = item.data
            else:
                data = getattr(item, 'data', data)

            if data:
                image_file = open(os.path.join(self.fsinfo.tmp_dir, filename) , 'wb')
                image_file.write(str(data))
                image_file.close()
        return


def makePDF(html, context, request):
    """Making the PDF from HTML
    """
    fsinfo = FileSystemInfo(context)
    parser = RecodeParser(fsinfo)
    html = parser.recode_data(html)
    parser.save_images(context)

    # Saving the HTML
    html_file = open(fsinfo.html_filename,'w')
    html_file.write(html.encode('iso-8859-15', 'replace'))
    html_file.close()

    # Building the PDF
    pdfbook_options = IPDFOptions(getSite())
    cmd = 'cd %s && %s %s %s > %s' % (
            fsinfo.tmp_dir,
            pdfbook_options.htmldoc_path,
            pdfbook_options.htmldoc_options,
            fsinfo.html_filename,
            fsinfo.pdf_filepath
            )
    logger.info(cmd)
    os.system(cmd)
    return fsinfo
