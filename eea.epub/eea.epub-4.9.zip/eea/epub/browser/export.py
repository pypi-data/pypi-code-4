""" Export as epub
"""

import os.path
from bs4 import BeautifulSoup
from StringIO import StringIO
from zipfile import ZipFile
import urlparse
import requests

from App.Common import package_home
from Products.Five import BrowserView
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter


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

    def handle_statics(self, zipFile, templateOutput):
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
                try:
                    resp = requests.get(url, cookies=self.request.cookies,
                                        timeout=5)
                except requests.exceptions.RequestException:
                    img.extract()
                    continue
                if resp.status_code == 200:
                    headers = resp.headers
                    itemid = 'image%05.d' % i
                    fname = "%s%s" % (itemid, url.strip('/').rsplit('/', 1)[-1])
                    zipFile.writestr('OEBPS/Images/%s' % fname, resp.content)
                    manifest.append(
                        '<item href="Images/%s" id="%s" media-type="%s"/>'
                        % (fname, itemid,
                           headers.get('content-type') or 'image/jpeg')
                    )
                    img['src'] = "Images/%s" % fname
                else:
                    img.extract()
            else:
                img.extract()

        for img in os.listdir(static_path("OEBPS/Images")):
            rel_path = "OEBPS/Images/%s" % img
            if not os.path.isfile(static_path(rel_path)):
                continue
            zipFile.writestr(rel_path, stream(rel_path))
            manifest.append('<item href="Images/%s" id="%s" media-type="%s"/>'
                            % (img, img, 'image/jpeg'))
        return (manifest, soup.prettify())

    def set_cover(self, zipFile):
        """ Look for image inside the object and set it as cover
        """
        if hasattr(self.context, "image_large"):
            image = self.context.image_large
            zipFile.writestr('OEBPS/Images/%s' % image.filename, image.data)
            return {
                'metadata': ['<meta name="cover" content="cover"/>'],
                'manifest': [
                    '<item href="Images/%s" id="cover" media-type="%s"/>' %
                    (image.filename, image.content_type)
                ]}
        else:
            return {'metadata': [], 'manifest': []}

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
        statics, templateOutput = self.handle_statics(zipFile, templateOutput)

        variables = {
            'TITLE': self.context.Title(),
            'IDENTIFIER': self.context.absolute_url(),
            'METADATA_MORE': '\n'.join(cover['metadata']),
            'MANIFEST_MORE': '\n'.join(cover['manifest'] + statics),
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
