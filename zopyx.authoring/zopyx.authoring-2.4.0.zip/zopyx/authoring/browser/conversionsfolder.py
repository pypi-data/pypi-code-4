####################################################################
# zopyx.authoring
# (C) 2010, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

import os
import shutil
import subprocess
import time
import tempfile
import zipfile
import json
import unicodedata
from ConfigParser import ConfigParser

import lxml.html

from DateTime import DateTime
from OFS.DTMLDocument import addDTMLDocument
from DateTime.DateTime import DateTime
from Products.Five.browser import BrowserView
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.ATContentTypes.interface.folder import IATFolder
from Products.ATContentTypes.interface.image import IATImage
from Products.ATContentTypes.interface.document import IATDocument
from Products.ATContentTypes.lib import constraintypes

from simpledropbox import SimpleDropbox
from zopyx.authoring import authoringMessageFactory as _
from zopyx.authoring.subscribers.events import BeforePublishing, AfterPublishing
from zopyx.smartprintng.plone.browser import util
from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
from plone.memoize import ram

import zope.event
import zope.component
from zope.interface import directlyProvides
from zope.contenttype import guess_content_type
try:
    from zope.pagetemplate.pagetemplatefile import PageTemplateFile
except ImportError:
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile as PageTemplateFile

from zopyx.smartprintng.plone.browser.splitter import split_html
import pp.client.python.pdf as pdf_client


from .. import HAVE_GHOSTSCRIPT
from ..logger import LOG
from ..config import PUBLISHED_DOCUMENT_CSS, CONVERSION_SERVER_URL
from ..interfaces import IConversionView

from zopyx.smartprintng.plone import Transformer, hasTransformations, availableTransformations
from util import safe_invokeFactory, preflight
import s5

# server host/port of the SmartPrintNG server
KEEP_OUTPUT = 'KEEP_OUTPUT' in os.environ

def fix_links(html, nodeid2filename):
    """ fix_links() is called for every splitted HTML document and will
        walk over all links referencing linkable components as
        given through href='resolveuid/<UID>#<id-or-anchor>'. It will lookup
        the referenced filename from the nodeid2filename dictionary
        and replace the href with a relative link to the real html file.
    """

    if not isinstance(html, unicode):
        html = unicode(html, 'utf-8')

    root = lxml.html.fromstring(html)
    for link in root.xpath('//*[name()="a"]'):
        href = link.attrib.get('href')
        if not href:
            continue

        ref_id = None
        if href.startswith('resolveuid') and '#' in href:
            ref_id = href.rsplit('#')[-1]
        elif href.startswith('#'):
            ref_id = href[1:] # chop of leading '#'

        if ref_id:
            ref_filename = nodeid2filename.get(ref_id)
            if ref_filename:
                link.attrib['href'] = '%s#%s' % (nodeid2filename[ref_id], ref_id)
            else:
                LOG.warn('No reference for %s found' % ref_id)
                link.attrib['class'] = link.attrib.get('class', '') + ' unresolved-link'

    return lxml.html.tostring(root, encoding=unicode)

class ConversionsFolderView(BrowserView):

    def __init__(self, context, request):
        self.request = request
        self.context = context
        self.export_run = False

    def redirect_edit_view(self):
        """ Redirect to edit view of the first document """

        content_folder = self.context.getContentFolder()
        brains = content_folder.getFolderContents({'portal_type' : 'AuthoringContentPage'})
        if len(brains) > 1:
            self.context.plone_utils.addPortalMessage(_(u'label_more_than_one_document_found', 
                                                        u'More than one editable document found. Please select a document from the content folder view.'), 
                                                        'error')
            return self.request.response.redirect(self.context.absolute_url())
        elif len(brains) == 0:
            self.context.plone_utils.addPortalMessage(_(u'label_no_document_found', 
                                                        u'No document found'), 
                                                        'error')
            return self.request.response.redirect(self.context.absolute_url())
        return self.request.response.redirect(brains[0].getURL() + '/edit')


    def _generate_pdf(self, **params):

        # merge request and method parameters
        LOG.info('generate_pdf() -> %r' % params)

        root_document = params.get('root_document', self.context.getContentFolder())
        transformations = params.get('transformations', [])[::]
        converter = params.get('converter', 'princexml')

        export_result = self.export_template_resources(params)
        LOG.info('  Export directory: %s' % export_result['workdir'])

        # get HTML body as snippet
        view = root_document.restrictedTraverse('@@asHTML')
        body = view(published_only=params.get('published-only'),
                    filter_uids=params.get('filter_uids', []))

        # the PDF rendering template is always exported as pdf_template.pt
        template_name = params.get('converter') == 'calibre' and 'ebook_template.pt' or 'pdf_template.pt'
        template_filename = os.path.join(export_result['workdir'], template_name)

        # now render the template
        html = PageTemplateFile(template_filename)(self.context,
                                                   context=self.context,
                                                   request=self.request,
                                                   content_root=root_document,
                                                   coverfront=export_result['coverfront'],
                                                   coverback=export_result['coverback'],
                                                   body=body)

        # apply transformations
        transformations.insert(0, 'ignoreHeadingsForStructure')
        transformations.append('adjustAnchorsToLinkables')
        transformations.append('fixAmpersand')

        LOG.info('Using new transformation engine (%s)' % transformations)
        T = Transformer(transformations, context=self.context, destdir=export_result['workdir'])
        html = T(html)

        # normalize to UTF (fixing issues with COMBINING DIAERESIS)
        html = unicodedata.normalize('NFC', html).encode('utf-8')
        html = html.replace(chr(11), ' ') # remove 0x0b crap chars

        html_output_filename = os.path.join(export_result['workdir'], 'index.html')
        file(html_output_filename, 'wb').write(html)

        errors = preflight(export_result['workdir'])
        for error in errors:
            LOG.warn('PREFLIGHT: %s' % error)

        if 'preflight_only' in params:
            return errors

        if 'no_conversion' in params:
            return export_result['workdir']

        # converter command line options
        if 'converter_commandline_options' in params:
            cmd_filename = os.path.join(export_result['workdir'], 'commandlineoptions.txt')
            file(cmd_filename, 'w').write(params['converter_commandline_options'])

        # run the conversion
        ts = time.time()
        LOG.info('Output written to %s' % export_result['workdir'])
        result = pdf_client.pdf(export_result['workdir'],
                                server_url=CONVERSION_SERVER_URL,
                                converter=params['converter'])

        if result['status'] != 'OK':
            raise RuntimeError('Conversion failed: {}'.format(result['output']))
                                          
        output_file = result['output_filename']
        LOG.info('Output filename: {}'.format(output_file))
        LOG.info('Output filesize: {} bytes'.format(os.path.getsize(output_file)))

        # reduce PDF size (if != 'default') by piping the pdf file through ghostscript
        pdf_quality = params.get('pdf_quality', 'default')
        if pdf_quality != 'default':
            dirname, basename = os.path.split(output_file)
            pdf_optimized = os.path.join(dirname, 'out_' + basename)
            cmd = 'gs -dCompatibilityLevel=1.4 -dPDFSETTINGS=/%s -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile="%s" "%s"' % (pdf_quality, pdf_optimized, output_file)
            LOG.info('Optimizing PDF (%s)' % cmd)
            p  = subprocess.Popen(cmd, shell=True)
            status = os.waitpid(p.pid, 0)[1]
            if status != 0:
                msg = u'PDF optimization failed with status %d' % status
                LOG.error(msg)
                raise RuntimeError(msg)
            result['output_filename'] = pdf_optimized

        LOG.info('Conversion time: %3.1f seconds' % (time.time() -ts))
        return result['output_filename']


    def _calibre_cmdline_options(self):
        """ Return Calibre conversion commandline options """

        cf = self.context.getContentFolder()
        params = {'title' : cf.Title().encode('utf-8'),
                  'authors' : u' & '.join(self.context.getEbookAuthors()),
                  'cover' : 'ebook-cover-image',
                 }
        return params

    def _calibre_additional_options(self):
        """ Inject additional Calibre options """
        options = list()
        options.append('--extra-css "%(WORKDIR)s/ebook.css"')
        if self.context.getEbookCoverpageImage():
            options.append('--cover "%(WORKDIR)s/ebook-cover-image"')
        if self.context.Subject():
            options.append('--tags "%s"' % u','.join(list(self.context.Subject())))
        if self.context.Language():
            options.append('--language %s' % self.context.Language())
        options.append('--book-producer "ZOPYX Produce and Publish AuthoringEnvironment"')
        return u' ' + u' '.join(options)

    def generate_epub(self, **kw):
        """ Browser view called directly from the P&P UI for generating
            an EPUB file.
        """

        params =  self.request.form
        params.update(kw)
        calibre_profile = self.context.getCalibreProfileObject()
        if calibre_profile is None:
            self.context.plone_utils.addPortalMessage(_(u'label_no_calibre_profile_configured', 
                                                        u'No Calibre file configured - unable to convert to EPUB'), 
                                                      'error')
            return self.request.response.redirect(self.context.absolute_url() + '?show_latest_draft=1')

        transformations = ['makeImagesLocal', 'cleanupForEPUB']
        params['converter'] = 'calibre'
        params['transformations'] = transformations
        params['converter_commandline_options'] = calibre_profile.getCommandlineOptions() % \
                                                  self._calibre_cmdline_options()
        params['converter_commandline_options'] += self._calibre_additional_options()
        return self.generate_pdf(**params)


    def generate_pdf(self, **kw):
        """ Browser view called directly from the P&P UI for generating
            a PDF file from the content in the configured content folder.
            The result will be stored inside the 'drafts' folder.
        """

        # merge request and keyword parameters
        params =  self.request.form
        params.update(kw)

        # call the PDF wrapper (returns PDF filename)
        output_file = self._generate_pdf(**params)
        if 'preflight_only' in params:
            return output_file # (which is actually 'errors')

        workdir = os.path.dirname(output_file)

        # optional ZIP conversion
        if params.has_key('store-zip'):
            zip_filename = tempfile.mktemp('.zip')
            ZF = zipfile.ZipFile(zip_filename, 'w')
            # add generated output file
            if output_file:
                ZF.write(output_file, os.path.basename(output_file))
            for filename  in os.listdir(workdir):
                ZF.write(os.path.join(workdir, filename), filename)
            ZF.close()
            output_file = zip_filename

        # guess content-type (ensure that this code will later also work with
        # other output formats)
        mime_type, enc = guess_content_type(output_file)
        basename, ext = os.path.splitext(os.path.basename(output_file))

        # store output file in local 'drafts' folder (hard-coded)
        dest_folder = self.context.drafts

        # limit name to 30 spaces since normalizeString() returns only 50 chars 
        # and we need space for the date-time string
        root_document = self.context.getContentFolder()
        dest_id = root_document.Title()[:30] + ' ' + DateTime().strftime('%Y-%m-%d-%H:%M:%S')
        dest_id = unicode(dest_id, 'utf-8')
        dest_id = IUserPreferredURLNormalizer(self.request).normalize(dest_id) + ext
        dest_folder.invokeFactory('File', id=dest_id, title=dest_id)
        dest_file = dest_folder[dest_id]
        dest_file.setFile(file(output_file, 'rb').read())
        dest_file.setContentType(mime_type)
        dest_file.reindexObject()

        # store conversion parameters as property (JSON)
        params_json = json.dumps(params)
        dest_file.manage_addProperty('conversionparameters', params_json, 'string')

        # store form parameters in session
        if hasattr(self.request, 'SESSION'):
            self.request.SESSION.set('zopyx_authoring', self.request.form.copy())

        if KEEP_OUTPUT:     
            LOG.info('Workdir: %s' % workdir)
            LOG.info('Outputfile: %s' % output_file)
        else:
            os.unlink(output_file)

        if not 'no_redirect' in kw:
            self.context.plone_utils.addPortalMessage(_(u'Output file generated'))
            self.request.response.redirect(self.context.absolute_url() + '?show_latest_draft=1')

    def generate_html_pdf(self, **kw):
        """ Browser view called directly from the P&P UI for generating
            HTML and optional PDF.
        """

        # merge request and keyword parameters
        params =  self.request.form
        params.update(kw)

        html_mode = params.get('html_mode', 'complete')
        target = params.get('target', 'drafts')
        content_folder = self.context.getContentFolder()

        # prepare destination
        if target == 'publications':
            # trigger archiving by sending an event#
            if 'do_archive' in params:
                zope.event.notify(BeforePublishing(self.context))

            dest_folder = self.context.getPublicationsFolder()
            for brain in dest_folder.getFolderContents():
                obj = brain.getObject()
                obj.unindexObject()
                dest_folder.manage_delObjects(obj.getId())

        else:
            dest_id = content_folder.Title()[:30] + ' ' + DateTime().strftime('%Y-%m-%d-%H:%M:%S')
            dest_id =  IUserPreferredURLNormalizer(self.request).normalize(dest_id)
            self.context.drafts.invokeFactory('Folder', id=dest_id, title=dest_id)
            dest_folder = self.context.drafts[dest_id]

        # store conversion parameters as property (JSON)
        params_json = json.dumps(params)
        if dest_folder.hasProperty('conversionparameters'):
            dest_folder._updateProperty('conversionparameters', params_json)
        else:
            dest_folder.manage_addProperty('conversionparameters', params_json, 'string')

        # export HTML + resource to the filesystem (but no conversion)
        workdir = self._generate_pdf(no_conversion=True,
                                     transformations=['makeImagesLocal',
                                                      'cleanupHtml',
                                                      'footnotesForHtml',
                                                      'rescaleImagesToOriginalScale',
                                                      'addAnchorsToHeadings',
                                                      'removeTableOfContents',
                                                      ])

        
        html_filename = os.path.join(workdir, 'index.html')

        # Post-transformation using new transformation API. Although the H2..H5
        # already carry id=".." attribute there are not attribute sets for the H1 nodes
        # since the H1 is usually taken from the document titles. The id attributes are only
        # added automatically by the ippcontent subscriber for the document body (having H2..H5
        # nodes)
        T = Transformer(['addUUIDs'])
        html = T(file(html_filename).read(), input_encoding='utf-8')
        file(html_filename, 'w').write(html.encode('utf-8'))

        # split always since we also need meta information from the main document
        split_html(html_filename)

        # There is always a documents.ini file generated by split_html()
        CP = ConfigParser()#
        CP.read(os.path.join(workdir, 'documents.ini'))

        # After calling split_html() the generated documents.ini will contain
        # information about all linkable objects inside each document. Each section of
        # document.ini will contain a list of 'node_ids'
        nodeid2filename = dict()    
        for section in CP.sections():
            node_ids = [nid.strip() for nid in CP.get(section, 'node_ids').split()]
            # determine of filename for current section            
            if html_mode == 'complete':
                filename = 'index.html' # all-in-one
            else:
                title = CP.get(section, 'title')
                filename = IUserPreferredURLNormalizer(self.request).normalize(unicode(title, 'utf-8'))
            for node_id in node_ids:
                nodeid2filename[node_id] = filename


        ################################################################
        # Store the (splitted) HTML inside drafts/publication folder
        ################################################################

        # import HTML files
        injected_styles = dict()

        countersStartWith = params.get('counter_start', 'h1')

        if html_mode == 'complete':
            # a single aggregated document is stored under 'index.html'
            id = 'index.html'
            CP.read(os.path.join(workdir, 'documents.ini'))
            title = CP.get('0', 'title')  # first document of split set

            html_filename = os.path.join(workdir, 'index.html')
            text = fix_links(file(html_filename).read(), nodeid2filename)
            dest_folder.invokeFactory('AuthoringPublishedDocument', id=id)
            page = dest_folder[id]
            page.setTitle(title)
            page.setCountersStartWith(countersStartWith)
            page.setText(text)
            page.setContentType('text/html')
            page.getField('text').setContentType(page, 'text/html')
            page.reindexObject()
            dest_folder.setDefaultPage(id)

            # inject office styles
            # retrieve the content document/page
            authoring_pages = content_folder.objectValues('AuthoringContentPage')
            if authoring_pages:
                page.setOfficeStyles(authoring_pages[0].getOfficeStyles())
            
        # now import splitted documents 
        elif html_mode == 'split':
            # for splitted documents we generate the HTML filename based
            # on the 'filename' option from the related sections

            table_counter = 0
            image_counter = 0
            sections = CP.sections()
            sections.sort(lambda x,y: cmp(int(x), int(y)))
            for i, section in enumerate(sections):
                filename = CP.get(section, 'filename')
                title = CP.get(section, 'title')
                id = IUserPreferredURLNormalizer(self.request).normalize(unicode(title, 'utf-8'))
                number_tables = CP.getint(section, 'number_tables')
                number_images = CP.getint(section, 'number_images')
                # inject split document specific counters
                if params.get('reset_counters'):
                    styles = ''
                else:
                    styles = PUBLISHED_DOCUMENT_CSS % dict(chapter_number=i,
                                                         image_counter=image_counter,
                                                         table_counter=table_counter)
                injected_styles[id] = styles.replace('#content', '#main-content')
                table_counter += number_tables
                image_counter += number_images
                text = fix_links(file(filename).read(), nodeid2filename)
                new_id = safe_invokeFactory(dest_folder,
                                            'AuthoringPublishedDocument', 
                                            id=id,
                                            title=title, 
                                            text=text,
                                            styles=styles,
                                            countersStartWith=countersStartWith,
                                            )
                dest_folder[new_id].setContentType('text/html')
                dest_folder[new_id].getField('text').setContentType(dest_folder[new_id], 'text/html')
                dest_folder[new_id].reindexObject()
                if i == 0:
                    dest_folder.setDefaultPage(new_id)

        ###########################################################################
        # Export presentation mode (making only sense with html_mode=complete)
        ###########################################################################

        if 'generate_s5' in params:
            id = 'index_s5.html'
            title = CP.get('0', 'title')  # first document of split set
            html_filename = os.path.join(workdir, 'index.html')
            s5_filename = s5.html2s5(self.context, html_filename)
            dest_folder.addDTMLDocument(id, id, file(s5_filename))

        ###########################################################################
        # import images (from $workdir/images.ini)
        ###########################################################################

        if os.path.exists(os.path.join(workdir, 'images.ini')):
            IMAGE_CP = ConfigParser()#
            IMAGE_CP.read(os.path.join(workdir, 'images.ini'))
            for section in IMAGE_CP.sections():
                filename = IMAGE_CP.get(section, 'filename')
                id = section
                description = title = u''
                if IMAGE_CP.has_option(section, 'title'):
                    title = IMAGE_CP.get(section, 'title')
                if IMAGE_CP.has_option(section, 'description'):
                    description = IMAGE_CP.get(section, 'description')
                if IMAGE_CP.has_option(section, 'id'):
                    id = IMAGE_CP.get(section, 'id')
                new_id = safe_invokeFactory(dest_folder, 
                                            'Image', 
                                            id=id,
                                            title=title,
                                            description=description,
                                            image=file(filename).read(),
                                            excludeFromNav=True)
                dest_folder[new_id].reindexObject()

        ###########################################################################
        # store aggregated HTML                
        ###########################################################################

        id = 'index_aggregated.html'
        title = CP.get('0', 'title')  # first document of split set
        html_filename = os.path.join(workdir, 'index.html')
        dest_folder.invokeFactory('Document', id=id)
        page = dest_folder[id]
        page.setTitle(title)
        page.setText(file(html_filename).read())
        page.setExcludeFromNav(True)
        page.reindexObject()

        ###########################################################################
        # now PDF generation
        ###########################################################################

        if 'generate_pdf' in params:

            # the published HTML already contains image captions other stuff
            # that we want remove first before running the PDF conversion.
            # In particular we need to export the images and re-created the captions
            transformations = ['removeListings',  # also removes image-captions
                               'removeProcessedFlags',
                               'makeImagesLocal', 
                               'addTableOfContents',
                               'addTableList',
                               'addImageList',
                              ]

            if html_mode == 'complete':
                output_filename = self._generate_pdf(root_document=dest_folder['index.html'],
                                                     reset_counters=1,                        
                                                     pdf_quality=params.get('pdf_quality', 'default'),
                                                     transformations=transformations)

                pdf_name = content_folder.Title()
                pdf_name = IUserPreferredURLNormalizer(self.request).normalize(pdf_name) + '.pdf'
                dest_folder.invokeFactory('File',
                                          id=pdf_name,
                                          title=pdf_name,
                                          file=file(output_filename).read())
                dest_folder[pdf_name].setFilename(pdf_name)
                dest_folder[pdf_name].setTitle(pdf_name)
                dest_folder[pdf_name].setFile(file(output_filename).read())

            elif html_mode == 'split':

                for brain in dest_folder.getFolderContents({'portal_type' : ('AuthoringPublishedDocument',)}):
                        transformations.append('replaceUnresolvedLinks')
                        root_document = brain.getObject()
                        output_filename = self._generate_pdf(root_document=root_document,
                                                             transformations=transformations,
                                                             reset_counters=1, # no need over carrying counters forward!?
                                                             pdf_quality=params.get('pdf_quality', 'default'),
#                                                             supplementary_stylesheet=styles_inject,
                                                             )

                        pdf_name = os.path.splitext(root_document.getId())[0] + '.pdf'
                        dest_folder.invokeFactory('File',
                                                  id=pdf_name,
                                                  title=pdf_name,
                                                  file=file(output_filename).read())
                        dest_folder[pdf_name].setFilename(pdf_name)

        ###########################################################################
        # generate EPub
        ###########################################################################

        if 'generate_epub' in params:
            transformations = ['removeListings', 'removeProcessedFlags', 'makeImagesLocal', 'cleanupForEPUB']
            params = dict()
            calibre_profile = self.context.getCalibreProfileObject()
            params['converter_commandline_options'] = ''
            if calibre_profile:
                params['converter_commandline_options'] = calibre_profile.getCommandlineOptions() % \
                                                          self._calibre_cmdline_options()
                params['converter_commandline_options'] += self._calibre_additional_options()

            params['root_document'] = dest_folder['index.html']
            params['converter'] = 'calibre'
            params['transformations'] = transformations
            params['reset_counters'] = 1

            output_filename = self._generate_pdf(**params)
            epub_source_html = os.path.join(os.path.dirname(output_filename), 'index.html')
            dest_folder.addDTMLDocument('index_epub.html', 'index_epub.html', file(epub_source_html))
            epub_name = 'index.epub'
            dest_folder.invokeFactory('File',
                                      id=epub_name,
                                      title=epub_name,
                                      file=file(output_filename).read())
            dest_folder[epub_name].setFilename(epub_name)
            dest_folder[epub_name].reindexObject()

        # AfterPublication hook (triggering) post-generation actions
        if target == 'publications':
            zope.event.notify(AfterPublishing(self.context))

        self.context.plone_utils.addPortalMessage(_(u'label_output_generated', 
                                                    u'Output file generated'))
        self.request.response.redirect(self.context.absolute_url() + '?show_latest_draft=1')

        if 'return_destination' in params:
            return dest_folder

    def export_template_resources(self, params):
        """ Export template resources to the filesystem (workdir) """

        template_folder = self.context.getConversionTemplate()
        template_folder.restrictedTraverse('@@sync')(redirect=False)
        content_folder = self.context.getContentFolder()
        prefix = '%s-%s-' % (self.context.getContentFolder().getId(), DateTime().ISO())
        workdir = tempfile.mkdtemp(prefix=prefix)

        # export template folder
        template_filename = None
        for obj in template_folder.getFolderContents():
            obj = obj.getObject()
            if obj.portal_type in ('AuthoringCoverPage', 'AuthoringCalibreProfile'):
                continue
            dest_filename = os.path.join(workdir, obj.getId())
            if obj.getId() == self.context.getMasterTemplate(): # id-by-reference
                dest_filename = template_filename = os.path.join(workdir, 'pdf_template.pt')
            if obj.getId() == self.context.getEbookMasterTemplate(): # id-by-reference
                dest_filename = template_filename = os.path.join(workdir, 'ebook_template.pt')
            # get_data() is a common API to all files under templates
            file(dest_filename, 'wb').write(obj.get_data())

        if template_filename is None:
            raise ValueError('No template "%s" found' % self.context.getMasterTemplate())

        # coverpage handling
        coverfront = coverback = None
        if params.get('use_front_cover_page') and self.context.getFrontCoverPage():
            cover_html = self.context.getFrontCoverPage().getHtml()
            tmp1 = tempfile.mktemp()
            file(tmp1, 'wb').write(cover_html)
            coverfront = PageTemplateFile(tmp1)(self.context,
                                                context=self.context,
                                                request=self.request,
                                                content_root=content_folder)
            os.unlink(tmp1)

        if params.get('use_back_cover_page') and self.context.getBackCoverPage():
            cover_html = self.context.getBackCoverPage().getHtml()
            tmp2 = tempfile.mktemp()
            file(tmp2, 'wb').write(cover_html)
            coverback = PageTemplateFile(tmp2)(self.context,
                                               context=self.context,
                                               request=self.request,
                                               content_root=content_folder)
            os.unlink(tmp2)

        # Ebook coverpage
        if self.context.getEbookCoverpageImage():
            file(os.path.join(workdir, 'ebook-cover-image'), 'wb').write(str(self.context.getEbookCoverpageImage().data))

        # supplementary stylesheet passed as text
        suppl_styles = params.get('supplementary_stylesheet', '')
        file(os.path.join(workdir, 'injected_counters.css'), 'w').write(suppl_styles)

        # inject office styles
        authoring_pages = [o for o in content_folder.contentValues() if o.portal_type == 'AuthoringContentPage']
        if authoring_pages:
            office_styles = authoring_pages[0].getOfficeStyles()
            file(os.path.join(workdir, 'injected_office_styles.css'), 'w').write(office_styles)

        return dict(workdir=workdir, coverfront=coverfront, coverback=coverback)


    def publishPublicationFolder(self):
        """ Publish all content in the configured publication folder """

        def publishWalker(obj):

            try:
                wf_tool.doActionFor(obj, 'publish')
                obj.reindexObject(idxs=['review_state'])
            except WorkflowException:
                pass

            if IATFolder.providedBy(obj):
                for brain in obj.getFolderContents():
                    publishWalker(brain.getObject())

        wf_tool = self.context.portal_workflow
        publication_folder = self.context.getPublicationsFolder()
        publishWalker(publication_folder)

    def publishDropbox(self, uid, rename=False):
        """ move a draft by UID to Dropbox """

        obj = self.context.portal_catalog(UID=uid)[0].getObject()
        username = self.context.getDropboxUsername()
        password = self.context.getDropboxPassword()
        directory = self.context.getDropboxDirectory()
        sdb = SimpleDropbox(username, password)
        sdb.login()
        if IATFolder.providedBy(obj):
            dest_path = unicode(directory + '/' + obj.getId() + '.zip')
            export_view = obj.restrictedTraverse('@@download_all')
            data = export_view(download=True)
            sdb.put(dest_path, data)
        else:
            dest_path = unicode(directory + '/' + obj.getId())
            sdb.put(dest_path, str(obj.getFile().data))
        self.context.plone_utils.addPortalMessage(_(u'Draft copied to Dropbox (%s@%s)' % (username, dest_path)))
        self.request.response.redirect(self.context.absolute_url() + '?show_latest_publication=1')

    def publishDraft(self, uid, rename=False):
        """ move a draft by UID from drafts to published folder """

        obj = self.context.portal_catalog(UID=uid)[0].getObject()
        cb = obj.aq_parent.manage_cutObjects([obj.getId()])
        dest = self.context.getPublicationsFolder()
        dest.manage_pasteObjects(cb)

        new_obj = dest[obj.getId()]
        new_id = new_obj.getId()
        if rename:
            basename, ext = os.path.splitext(new_id)
            dest_id =  IUserPreferredURLNormalizer(self.request).normalize(self.context.getContentFolder().Title()) + ext
            if dest_id in dest.objectIds():
                dest.manage_delObjects(dest_id)
            dest.manage_renameObject(new_id, dest_id)
            new_obj = dest[dest_id]
            new_obj.setTitle(self.context.getContentFolder().Title())
            new_obj.reindexObject()

        if new_obj.portal_type == 'File':
            new_obj.setFilename(new_id)

        # try to publish
        try:
            self.context.portal_workflow.doActionFor(new_obj, 'publish')
        except WorkflowException:
            LOG.warn('Unable to change wfstate to publish for draft (%s)' % (new_obj.absolute_url(1)))

        self.context.plone_utils.addPortalMessage(_(u'Draft published'))
        self.request.response.redirect(self.context.absolute_url() + '?show_latest_publication=1')

    def cleanDrafts(self):
        """ remove all drafts """

        self.context.drafts.manage_delObjects(self.context.drafts.objectIds())
        self.context.plone_utils.addPortalMessage(_(u'Drafts folder cleaned'))
        self.request.response.redirect(self.context.absolute_url())

    def availableTransformations(self):
        """ return all available transformations """
        return availableTransformations()

    def relativePath(self, obj):
        """ return relative path of object within Plone site """
        obj_path = '/'.join(obj.getPhysicalPath())
        plone_path = '/'.join(self.context.portal_url.getPortalObject().getPhysicalPath()) + '/'
        return obj_path.replace(plone_path, '')

    def getSupplementaryConversionViews(self):
        result = list()
        for name, util in zope.component.getUtilitiesFor(IConversionView):
            d = util()
            d['name'] = name
            result.append(d)
        return result

    def getCalibreProfiles(self):
        """ Return calibre profiles from authoring project parent """
        return ()

    def haveGhostscript(self):
        """ Ghostscript installed? """
        return HAVE_GHOSTSCRIPT

    def getContentFolderContents(self):
        """ Return content of the content folder """
        content_folder = self.context.getContentFolder()
        return content_folder.getFolderContents({'portal_type' : ('Document', 'AuthoringContentPage')})

