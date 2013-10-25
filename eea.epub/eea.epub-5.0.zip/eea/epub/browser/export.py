""" Export as epub
"""

import os.path
from bs4 import BeautifulSoup
from StringIO import StringIO
from zipfile import ZipFile
import urlparse
import requests
import logging
import re

from App.Common import package_home
from Products.Five import BrowserView
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter, queryUtility

from eea.converter.utils import absolute_url
from eea.converter.interfaces import IConvert


logger = logging.getLogger('eea.epub')


def slugify(title):
    """ Very basic slugify for ids or filenames
    """
    return re.sub(r'[^a-zA-Z0-9\.]', '_', title)


def static_path(filePath):
    """ Return abs path of a static file named `filename` which is available
    inside the static folder available in this package for the epub tpl
    """
    return os.path.join(package_home(globals()), 'static', filePath)


def replace(filePath, variables):
    """ Replaces content from a file with given variables
    """
    filePath = static_path(filePath)
    f = open(filePath)
    content = f.read()
    f.close()
    return content % variables


def stream(filePath):
    """ Same as `replace`, but no text handling, simply bytestream the data
    """
    filePath = static_path(filePath)
    f = open(filePath, "rb")
    content = f.read()
    f.close()
    return content


class ExportView(BrowserView):
    """ ExportView Browserview
    """
    template = ViewPageTemplateFile('epub.pt')

    def abs_url(self, image_source):
        """ Return abs URL out of a `src` img attribute
        """
        if image_source.startswith(('http:', 'https:')):
            return image_source
        else:
            ctxt_state = getMultiAdapter((self.context.aq_inner, self.request),
                                         name=u'plone_context_state')
            ob_url = ctxt_state.object_url()
            if image_source.startswith('/'):
                return urlparse.urljoin(ob_url, image_source)
            else:
                return urlparse.urljoin("%s/" % ob_url, image_source)

    def store_image(self, zipFile, url, itemid, filename=''):
        """ Given an URL to an image, save it in zip and return path
        """
        try:
            resp = requests.get(url, cookies=self.request.cookies, timeout=5)
        except requests.exceptions.RequestException:
            return ('', '')
        if resp.status_code == 200:
            headers = resp.headers
            if not filename:
                filename = "%s%s" % (itemid, url.strip('/').rsplit('/', 1)[-1])
                filename = slugify(filename)
            zipFile.writestr('OEBPS/Images/%s' % filename, resp.content)
            return ("Images/%s" % filename,
                    '<item href="Images/%s" id="%s" media-type="%s"/>'
                    % (filename, itemid,
                       headers.get('content-type') or 'image/jpeg'))
        else:
            return ('', '')

    def handle_statics(self, templateOutput, zipFile):
        """
        * Embedding images: looks for referenced images in content
        and properly save them in the epub
        * Style related images available in eea.epub template

        """
        manifest = []
        soup = BeautifulSoup(templateOutput)
        imgs = soup.find_all("img")
        for i, img in enumerate(imgs):
            if img.get('src'):
                url = self.abs_url(img['src'])
                itemid = 'image%05.d' % i
                src, manifest_entry = self.store_image(zipFile, url, itemid)
                if src:
                    img['src'] = src
                    manifest.append(manifest_entry)
                else:
                    img.extract()
        for img in os.listdir(static_path("OEBPS/Images")):
            rel_path = "OEBPS/Images/%s" % img
            if not os.path.isfile(static_path(rel_path)):
                continue
            zipFile.writestr(rel_path, stream(rel_path))
            manifest.append('<item href="Images/%s" id="%s" media-type="%s" />'
                            % (img, img, 'image/jpeg'))
        return (soup, manifest)

    def set_cover(self, zipFile):
        """ Look for image inside the object and set it as cover
        """
        pdf_adapt = getMultiAdapter((self.context.aq_inner, self.request),
                                    name="download.pdf")
        pdf_file = pdf_adapt.make_pdf_cover()
        converter = queryUtility(IConvert)
        data = converter(None, path_from=pdf_file)
        try:
            os.unlink(pdf_file)
        except Exception, err:
            logger.warn(err)

        zipFile.writestr('OEBPS/Images/%s' % "cover.png", data)
        return {
            'metadata': ['<meta name="cover" content="cover"/>'],
            'manifest': [
                '<item href="Images/%s" id="cover" media-type="%s" />' %
                ("cover.png", "image/png")
            ]}

    def set_toc(self, soup):
        """
        Build the table of contents for toc.ncx and return it
        as xml utf-8 string.
        Headings Level 2 are used to generate the table of contents.

        """
        chapters = []
        chapter_tpl = u"""
                      <navPoint id="navpoint-%(i)d" playOrder="%(i)d">
                        <navLabel>
                          <text>%(title)s</text>
                        </navLabel>
                        <content src="content.xhtml#%(offset)s"/>
                      </navPoint>"""
        for (i, h2) in enumerate(soup.find_all("h2")):
            title = h2.text
            offset = h2.get("id") or "%s_%d" % (slugify(title), i)
            chapters.append((title, offset))
            h2['id'] = offset
        if not chapters:
            h1 = soup.find("h1")
            if h1 and h1.text:
                chapters.append((h1.text, ''))
            else:
                chapters.append(('Content', ''))
        chap_xmls = [chapter_tpl % ({'title': title,
                                     'i': (i + 1),
                                     'offset': offset})
                     for (i, (title, offset)) in enumerate(chapters)]
        return u"\n".join(chap_xmls).encode("utf-8")

    def fix_daviz(self, soup, zipFile):
        """
        Replace Daviz iframe with fallback images.
        Must be called AFTER `handle_statistics`.

        """
        manifest = []
        for (i, iframe) in enumerate(soup.find_all('iframe')):
            src = iframe.get('src')
            if u'embed-chart' in src:
                src = src.replace('embed-chart', 'embed-chart.png')
                src = absolute_url(self.context,
                        url=src, default=src, view='embed-chart.png')
                base = src.split('embed-chart.png')[0]
                query = urlparse.parse_qs(urlparse.urlparse(src).query)
                chart = query.get('chart')[0]
            elif u'embed-dashboard' in src:
                src = src.replace('embed-dashboard', 'embed-dashboard.png')
                src = absolute_url(self.context,
                        url=src, default=src, view='embed-dashboard.png')
                base = src.split('embed-dashboard.png')[0]
                query = urlparse.parse_qs(urlparse.urlparse(src).query)
                chart = query.get('dashboard')[0]
            else:
                continue

            src += '&tag:int=0&safe:int=0'

            if not src.startswith('http'):
                src = os.path.join(self.context.absolute_url(), src)
            if not base.startswith('http'):
                base = os.path.join(self.context.absolute_url(), base)

            img_src = ''
            try:
                resp = requests.get(src, cookies=self.request.cookies,
                                    timeout=5)
            except Exception, err:
                logger.exception(err)
            else:
                if resp.status_code == 200:
                    itemid = 'daviz%02.d' % i
                    fname = "%s.png" % itemid
                    img_src, manifest_item = self.store_image(zipFile, src,
                                                              itemid, fname)
            if img_src:
                iframe.replaceWith(
                    BeautifulSoup("<img src='%s' />" % img_src).find("img"))
                manifest.append(manifest_item)
            else:
                chart_url = u'%s#tab-%s' % (base, chart)
                message = BeautifulSoup(u'''
                <div class="portalMessage warningMessage pdfMissingImage">
                  <span>
                    This area contains interactive content
                    which can not be displayed in an e-book.
                    You may visit the online version at:
                  </span>
                  <a href="%(url)s">%(url)s</a>
                </div>''' % {'url': chart_url})
                iframe.replaceWith(message)
        return (soup, manifest)

    def __call__(self):
        response = self.request.response
        response.setHeader('Content-Type', 'application/xml+epub')
        response.setHeader(
                'Content-Disposition', 'attachment; filename=%s.epub' %
                                                                self.context.id)

        templateOutput = self.template(self)
        # This encoding circus was required for including context.getText() 
        # in the template
        if not isinstance(templateOutput, unicode):
            templateOutput = templateOutput.decode('utf-8')
        inMemoryOutputFile = StringIO()
        zipFile = ZipFile(inMemoryOutputFile, 'w')

        cover = self.set_cover(zipFile)
        soup, statics = self.handle_statics(templateOutput, zipFile)
        soup, daviz = self.fix_daviz(soup, zipFile)
        toc = self.set_toc(soup)
        templateOutput = soup.prettify()

        variables = {
            'TITLE': self.context.Title(),
            'IDENTIFIER': self.context.absolute_url(),
            'METADATA_MORE': '\n'.join(cover['metadata']),
            'MANIFEST_MORE': '\n'.join(cover['manifest'] + statics + daviz),
            'TOC': toc,
        }

        zipFile.writestr('mimetype', 'application/epub+zip')
        zipFile.writestr('META-INF/container.xml',
                         stream('META-INF/container.xml'))

        zipFile.writestr('OEBPS/content.xhtml', templateOutput.encode("utf-8"))
        zipFile.writestr('OEBPS/Css/main.css', stream("OEBPS/Css/main.css"))
        zipFile.writestr('OEBPS/content.opf', replace(
                                            'OEBPS/content.opf', variables))
        zipFile.writestr('OEBPS/toc.ncx', replace('OEBPS/toc.ncx', variables))
        zipFile.close()

        inMemoryOutputFile.seek(0)
        return inMemoryOutputFile.read()
