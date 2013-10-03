#####################################################################
# zopyx.authoring
# (C) 2011, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

import os
import tempfile
import zipfile

from Products.Five.browser import BrowserView
from zopyx.authoring import authoringMessageFactory as _


HTML = """
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<link rel="stylesheet" href="publisheddocument.css" type="text/css" />
<link rel="stylesheet" href="publisheddocument_counters_h1.css" type="text/css" />
<style type="text/css">
%(styles)s
</style>
</head>
<body>
<div id="content">
%(html)s        
</div>
</body>
</html>
"""

package_home = os.path.dirname(__file__)
published_css = file(os.path.join(package_home, 'resources', 'publisheddocument.css')).read()
published_h1_css = file(os.path.join(package_home, 'resources', 'publisheddocument_counters_h1.css')).read()
published_h2_css = file(os.path.join(package_home, 'resources', 'publisheddocument_counters_h2.css')).read()

class DownloadAll(BrowserView):
    """ Download all content of folder as ZIP """

    def __call__(self, download=False):

        try:
            self.context.getAuthoringProject()
        except AttributeError:
            self.request.response.setStatus(404)
            return

        have_s5 = 'index_s5.html' in self.context.objectIds()
        have_epub = 'index.epub' in self.context.objectIds()

        # Write ZIP archive
        zip_filename = tempfile.mktemp()
        ZIP = zipfile.ZipFile(zip_filename, 'w')
        # CSS first
        ZIP.writestr('html/publisheddocument.css', published_css)
        ZIP.writestr('html/publisheddocument_counters_h1.css', published_h1_css)
        ZIP.writestr('html/publisheddocument_counters_h2.css', published_h2_css)

        html_filenames = list()
        for obj in self.context.getFolderContents():
            obj = obj.getObject()
            obj_id = obj.getId()

            if obj.portal_type in ('AuthoringPublishedDocument',):
                styles = obj.getStyles()
                html = obj.getText()
                html = html.replace('/image_preview', '')
                html = HTML % dict(html=html, styles=styles)
                id = 'html/' + obj_id
                if not id.endswith('.html'):
                    id += '.html'
                ZIP.writestr(id, html)
                html_filenames.append(id)

            elif obj.portal_type in ('Document',): # S5
                if obj_id == 'index_aggregated.html':
                    html = obj.getText()
                    html = html.replace('/image_preview', '')
                    html = HTML % dict(html=html, styles='')
                    ZIP.writestr('html/index_aggregated.html', html)

            elif obj.portal_type == 'Image':
                # export only preview scale
                img = obj.Schema().getField('image').getScale(obj, scale='preview')
                if img is not None: # TQM workaround
                    ZIP.writestr('html/' + obj_id, str(img.data))
                    ZIP.writestr('presentation/%s/image_preview' % obj_id, str(img.data))
                    if have_epub:
                        ZIP.writestr('epub/preview_%s' % obj_id, str(img.data))

            elif obj.portal_type == 'File':
                if obj.getId().endswith('.pdf'):
                    ZIP.writestr('pdf/' + obj.getId(), str(obj.getFile().data))
                elif obj.getId().endswith('.epub'):
                    ZIP.writestr('epub/' + obj_id, str(obj.getFile().data))

        if html_filenames:
            ZIP.writestr('html/all-files.txt', '\n'.join(html_filenames))

        # Further EPUB stuff
        if have_epub:
            obj = self.context['index_epub.html']
            ZIP.writestr('epub/index_epub.html', obj.document_src())

        # S5 export                                          
        # The S5 HTML document is stored as a DTML Document. All other resources are
        # located in the skins folder and are acquired here using acquisition
        if have_s5:
            obj = self.context['index_s5.html']
            ZIP.writestr('presentation/index.html', obj.document_src())

            # S5 Resources
            for name in ('pp-s5-core.css',
                         'pp-s5-framing.css',
                         'pp-s5-opera.css',
                         'pp-s5-outline.css',
                         'pp-s5-pretty.css',
                         'pp-s5-print.css',
                         'pp-s5-pretty.css',
                         'pp-s5-slides.css',
                         'pp-s5-slides.js'):
                resource = getattr(self.context, name)
                ZIP.writestr('presentation/%s' % name, str(resource))

            # custom immages
            for name in ('logo.png', 'custom-logo.png', 'title.png'):
                img = getattr(self.context, name, None)
                if img:
                    ZIP.writestr('presentation/%s' % name, str(img._data))

        ZIP.close()

        data = file(zip_filename).read()
        if download:
            return data
        os.unlink(zip_filename) 
        R = self.request.RESPONSE
        R.setHeader('content-type', 'application/zip')
        R.setHeader('content-length', len(data))
        R.setHeader('content-disposition', 'attachment; filename="%s.zip"' % self.context.getId())
        return R.write(data)


class SortFolderView(BrowserView):
    """ Sort folder alphabatically """

    def __call__(self):

        docs = list(self.context.getFolderContents())
        docs.sort(lambda x,y: cmp(x.Title, y.Title))
        for i, brain in enumerate(docs):
            self.context.moveObjectToPosition(brain.getId, i)
            self.context[brain.getId].reindexObject()

        self.context.plone_utils.addPortalMessage(_(u'label_folder_sorted', u'Folder sorted'))
        self.request.response.redirect(self.context.absolute_url())
