#####################################################################
# zopyx.authoring
# (C) 2010, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

import os
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from DateTime.DateTime import DateTime
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.i18n.normalizer.de import Normalizer

from .. import authoringMessageFactory as _

package_home = os.path.dirname(__file__)

class AuthoringProject(BrowserView):

    def add_authoringproject(self, title):
        """ Prepare AuthoringEnvironment for a new project """

        putils = getToolByName(self.context, 'plone_utils')
        project_id = Normalizer().normalize(unicode(title, 'utf-8').lower())
        project_id = putils.normalizeString(project_id)

        if not 'contents' in self.context.objectIds():
            self.context.invokeFactory('AuthoringContentsFolder', id='contents', title='Contents')
            self.context['contents'].reindexObject()

        if not 'templates' in self.context.objectIds():
            self.context.invokeFactory('AuthoringTemplatesFolder', id='templates', title='Templates')
            self.context['templates'].reindexObject()

            # setup demo template folder
            templates = self.context['templates']
            templates.invokeFactory('AuthoringTemplate', id='template', title='Template')
            demo_template = templates['template']
            demo_template.restrictedTraverse('@@import_resource')('pp-default', import_mode='clear')

        if not 'conversions' in self.context.objectIds():
            self.context.invokeFactory('AuthoringConversionsCollection', id='conversions', title='Conversions')
            self.context['conversions'].reindexObject()

        # setup demo content
        contents = self.context['contents']
        if project_id in contents.objectIds():
            self.context.plone_utils.addPortalMessage(_(u'label_project_exists', u'Project already exists - choose a different name'), 'error')
            return self.request.response.redirect(self.context.absolute_url())                                                             

        contents.invokeFactory('AuthoringContentFolder', id=project_id)
        demo = contents[project_id]
        demo.setTitle(title)
        demo.reindexObject()
        demo.invokeFactory('AuthoringContentPage', 'page1', title='Page1')
        page1 = demo['page1']
        page1.setTitle(u'Page1')
        page1.setDescription(u'Test document')
        page1.setText(file(os.path.join(package_home, 'default.txt')).read())
        page1.setFormat('text/html')
        page1.setContentType('text/html')
        page1.reindexObject()

        # prepare conversions folder   
        conversions_collection = self.context['conversions']
        conversions_collection.invokeFactory('AuthoringConversionFolder', id=project_id)
        conversion = conversions_collection[project_id]
        conversion.setTitle(title)
        conversion.reindexObject()
        conversion.setContentFolderPath('/'.join(demo.getPhysicalPath()))
        templates = self.context['templates']
        demo_template = templates['template']
        conversion.setConversionTemplatePath('/'.join(demo_template.getPhysicalPath()))
        conversion.setPublicationsFolder(conversion['published'])
        conversion.setMasterTemplate('pdf_template.pt')
        conversion.setEbookMasterTemplate('ebook_template.pt')
        conversion.setCalibreProfile('calibre_profile.calibre')
        conversion.setStyles([
                    'styles_standalone.css',
                    'single_aggregated_bookmarks.css',
                    'single_aggregated_toc.css',
                    'page_numbers.css',
                    'hyphenation.css',
                    'footnotes.css',
                    'images.css',
                    'tables.css',
                    'crossreferences.css',
                    'indexes.css',
                    ]),

        self.context.plone_utils.addPortalMessage(_(u'label_project_created', u'Project created'))
        self.request.response.redirect(conversion.absolute_url())


    def cleanup_project(self, drafts_older_than=0):
        """ Remove drafts older than N days """

        ct = getToolByName(self.context, 'portal_catalog')
        now = DateTime()
        path = '/'.join(self.context.getPhysicalPath())
        for brain in ct(portal_type='AuthoringConversionFolder', path=path):
            conv = brain.getObject()
            del_ids = [ob.getId for ob in conv.drafts.getFolderContents() if now - ob.modified > drafts_older_than]
            conv.drafts.manage_delObjects(del_ids)

        self.context.plone_utils.addPortalMessage(_(u'label_project_cleanup_down', u'Cleanup done'))
        self.request.response.redirect(self.context.absolute_url())

