#####################################################################
# zopyx.authoring
# (C) 2010, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

"""Definition of the AuthoringConversionFolder content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.CMFCore.utils import getToolByName

from zopyx.authoring import authoringMessageFactory as _
from zopyx.authoring.interfaces import IAuthoringConversionFolder
from zopyx.authoring.config import PROJECTNAME
from zopyx.authoring.widget import SortableInAndOutWidget

from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget

from util import invisibleFields

AuthoringConversionFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    atapi.StringField('contentFolderPath',
                       vocabulary='getAvailableContentFolders',
                       widget=atapi.SelectionWidget(label=_('label_contents_folder', default='Contents folder'),
                                                    format='select',
                                                   )
                  ),

    atapi.StringField('conversionTemplatePath',
                       vocabulary='getAvailableAuthoringTemplates',
                       widget=atapi.SelectionWidget(label=_('label_template_folder', default='Template folder'),
                                                    format='select',
                                                   )
                  ),

    atapi.StringField('coverpageFrontPath',
                       vocabulary='getAvailableCoverPages',
                       widget=atapi.SelectionWidget(label=_('label_cover_frontpage', default='Front cover page'),
                                                    format='select',
                                                   )
                  ),

    atapi.StringField('coverpageBackPath',
                       vocabulary='getAvailableCoverPages',
                       widget=atapi.SelectionWidget(label=_('label_cover_backpage', default='Back cover page'),
                                                    format='select',
                                                   )
                  ),


    atapi.ReferenceField('publicationsFolder',
                     relationship='usePublications',
                     allowed_types=('Folder',),
                     widget=ReferenceBrowserWidget(label=_('label_publications_folder', default='Publications folder'),
                                                   force_close_on_insert=1,
                                                   )
                  ),

    atapi.ReferenceField('archiveFolder',
                     relationship='archivedIn',
                     allowed_types=('Folder',),
                     widget=ReferenceBrowserWidget(label=_('label_archive_folder', default='Archive folder'),
                                                   force_close_on_insert=1,
                                                   )
                  ),

    atapi.StringField('masterTemplate',
                    vocabulary='getAvailableMasterTemplates',
                    widget=atapi.SelectionWidget(label=_('label_master_template', 'Master template')),
                    ),

    atapi.LinesField('styles',
                    vocabulary='getAvailableStyles',
                    widget=atapi.MultiSelectionWidget(label=_('label_stylesheets', 'Stylesheets'),
                                           
                                               size=20,
                                               )
                    ),

################################################
# Ebook
################################################

    atapi.StringField('calibreProfile',
                    schemata='ebook',
                    vocabulary='getCalibreProfiles',
                    widget=atapi.SelectionWidget(label=_('label_calibre_profile', 'Calibre profile')),
                    ),
    atapi.StringField('ebookMasterTemplate',
                    vocabulary='getAvailableMasterTemplates',
                    schemata='ebook',
                    widget=atapi.SelectionWidget(label=_('label_ebook_master_template', 'Master template for ebooks')),
                    ),
    atapi.LinesField('ebookAuthors',
                    default=(),
                    schemata='ebook',
                    widget=atapi.LinesWidget(label=_('label_ebook_authors', 'Authors (one per line)')),
                    ),
    atapi.ImageField('ebookCoverpageImage',
                    schemata='ebook',
                    widget=atapi.ImageWidget(label=_('label_ebook_coverpage_image', 'Coverpage image')),
                    ),

################################################
# S5 
################################################

    atapi.StringField('s5Line1',
                    default='',
                    schemata='s5',
                    widget=atapi.StringWidget(label=_('label_s5_line1', default='S5 line 1'), 
                                              size=60),
                    ),
    atapi.StringField('s5Line2',
                    default='',
                    schemata='s5',
                    widget=atapi.StringWidget(label=_('label_s5_line2', default='S5 line 2'), 
                                              size=60),
                    ),
    atapi.StringField('s5Line3',
                    default='',
                    schemata='s5',
                    widget=atapi.StringWidget(label=_('label_s5_line3', default='S5 line 3'), 
                                              size=60),
                    ),
    atapi.StringField('s5Line4',
                    default='',
                    schemata='s5',
                    widget=atapi.StringWidget(label=_('label_s5_line4', default='S5 line 4'), 
                                              size=60),
                    ),
################################################
# Dropbox
################################################

    atapi.BooleanField('dropboxEnabled',
                    default=False,
                    schemata='dropbox',
                    widget=atapi.BooleanWidget(label=_('label_dropbox_enabled', default='Dropbox enabled') 
                                              ),
                    ),

    atapi.StringField('dropboxUsername',
                    default='',
                    schemata='dropbox',
                    widget=atapi.StringWidget(label=_('label_dropbox_username', default='Dropbox username'), 
                                              size=20),
                    ),

    atapi.StringField('dropboxPassword',
                    default='',
                    schemata='dropbox',
                    widget=atapi.StringWidget(label=_('label_dropbox_password', default='Dropbox password'), 
                                              size=20),
                    ),

    atapi.StringField('dropboxDirectory',
                    default='',
                    schemata='dropbox',
                    widget=atapi.StringWidget(label=_('label_dropbox_directory', default='Dropbox directory'), 
                                              size=80),
                    ),

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

AuthoringConversionFolderSchema['title'].storage = atapi.AnnotationStorage()
AuthoringConversionFolderSchema['description'].storage = atapi.AnnotationStorage()

invisibleFields(AuthoringConversionFolderSchema, 
                'allowDiscussion', 'nextPreviousEnabled',
                'excludeFromNav', 'subject', 'location', 
                'creators', 'contributors', 'rights',
                'language', 'effectiveDate', 'expirationDate')

schemata.finalizeATCTSchema(
    AuthoringConversionFolderSchema,
    folderish=True,
    moveDiscussion=False
)

class AuthoringConversionFolder(folder.ATFolder):
    """Authoring Conversion Folder"""
    implements(IAuthoringConversionFolder)

    meta_type = "AuthoringConversionFolder"
    schema = AuthoringConversionFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    def manage_afterAdd(self, item, container):
        super(folder.ATFolder, self).manage_afterAdd(item, container)
        if not 'drafts' in self.objectIds():
            self.invokeFactory('Folder', id='drafts', title='Drafts')
        if not 'published' in self.objectIds():
            self.invokeFactory('Folder', id='published', title='Published')

    def getConversionFolder(self):
        """ Return me :-) """
        return self

    def getAvailableStyles(self):
        """ Available stylesheets from conversions folder """
        vocab = atapi.DisplayList()
        folder = self.getConversionTemplate()
        if not folder:
            return ()
        for brain in folder.getFolderContents(contentFilter=dict(portal_type='AuthoringStylesheet', sort_on='sortable_title')):
            title = brain.Title
            if brain.getId != brain.Title:
                title += ' (ID: %s)' % brain.getId            
            vocab.add(brain.getId, title)
        return vocab

    def getCalibreProfiles(self):
        """ Available stylesheets from conversions folder """
        vocab = atapi.DisplayList()
        folder = self.getConversionTemplate()
        if not folder:
            return ()
        for brain in folder.getFolderContents(contentFilter=dict(portal_type='AuthoringCalibreProfile', sort_on='sortable_title')):
            title = brain.Title
            if brain.getId != brain.Title:
                title += ' (ID: %s)' % brain.getId            
            vocab.add(brain.getId, title)
        return vocab

    def getAvailableMasterTemplates(self):
        """ Available master templates from conversions folder """

        vocab = atapi.DisplayList()
        folder = self.getConversionTemplate()
        if not folder:
            return ()
        for brain in folder.getFolderContents(contentFilter=dict(portal_type='AuthoringMasterTemplate')):
            title = brain.Title
            if brain.getId != brain.Title:
                title += ' (ID: %s)' % brain.getId            
            vocab.add(brain.getId, title)
        return vocab

    ############################################################
    # Vocabulary helper methods folder
    ############################################################

    def _defCandidates(self, portal_type, with_omit=False, exclude_ids=[]):
        vocab = atapi.DisplayList()
        if with_omit:
            vocab.add('', _('label_no_cover_page', '-no cover page-'))

        catalog = getToolByName(self, 'portal_catalog')
        ap_path = '/'.join(self.getAuthoringProject().getPhysicalPath())
        for brain in catalog(portal_type=portal_type,
                             path=ap_path, sort_on='sortable_title'):

            if brain.getId in exclude_ids:
                continue
            title = '%s (%s)' % (brain.Title, brain.portal_type)
            vocab.add(brain.getPath(), title)
        return vocab

    def getAvailableContentFolders(self):
        return self._defCandidates(('AuthoringContentFolder', 'Folder'), exclude_ids=('published', 'drafts'))

    def getAvailableAuthoringTemplates(self):
        return self._defCandidates('AuthoringTemplate')

    def getAvailableCoverPages(self):
        return self._defCandidates('AuthoringCoverPage', with_omit=True)

    def getConversionTemplate(self):
        if not self.getConversionTemplatePath():
            return
        return self.restrictedTraverse(self.getConversionTemplatePath(), None)

    def getContentFolder(self):
        if not self.getContentFolderPath():
            return
        return self.restrictedTraverse(self.getContentFolderPath(), None)

    def getFrontCoverPage(self):
        if not self.getCoverpageFrontPath():
            return
        return self.restrictedTraverse(self.getCoverpageFrontPath(), None)

    def getBackCoverPage(self):
        if not self.getCoverpageBackPath():
            return
        return self.restrictedTraverse(self.getCoverpageBackPath(), None)

    def getCalibreProfileObject(self):
        if not self.getCalibreProfile():
            return
        return self.getConversionTemplate().restrictedTraverse(self.getCalibreProfile(), None)

atapi.registerType(AuthoringConversionFolder, PROJECTNAME)
