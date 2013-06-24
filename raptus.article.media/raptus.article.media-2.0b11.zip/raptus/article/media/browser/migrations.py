import os
from Acquisition import aq_inner
from zope.annotation.interfaces import IAnnotations

from plone.app.blob.migrations import haveContentMigrations
from plone.app.blob.browser.migration import ImageMigrationView
from plone.app.blob.browser.migration import __file__ as location
from plone.app.blob.migrations import ATImageToBlobImageMigrator
from plone.app.blob.migrations import migrate
from plone.app.blob.migrations import getMigrationWalker

from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _


class ArticleMediaToBlobImageMigrator(ATImageToBlobImageMigrator):
    
    src_portal_type = 'Video'
    src_meta_type = 'Video'
    dst_portal_type = 'Video'
    dst_meta_type = 'Video'

    fields = ['file', 'image']
    
    def migrate_data(self):
        for field in self.fields:
            annotations = IAnnotations(self.old)
            res = annotations.get('Archetypes.storage.AnnotationStorage-%s'%field, None)
            if res:
                if field == 'file':
                    field = self.new.Schema()[field]
                    field.getMutator(self.new)(res)
                else:
                    self.new.Schema()[field].set(self.new, res)
                    del annotations['Archetypes.storage.AnnotationStorage-%s'%field]

    def createNew(self):
        self.new = self.old
        
    def remove(self):
        pass

    def reorder(self):
        pass
    
    def renameOld(self):
        pass

class ArticleAudioToBlobMigrator(ArticleMediaToBlobImageMigrator):

    src_portal_type = 'Audio'
    src_meta_type = 'Audio'
    dst_portal_type = 'Audio'
    dst_meta_type = 'Audio'
    fields = ['file']


class ArticleMediaMigrationView(ImageMigrationView):
    
    index = ViewPageTemplateFile('%s/migration.pt' % os.path.dirname(location))
    
    def __call__(self):
        context = aq_inner(self.context)
        request = aq_inner(self.request)
        walkers = self.walkers()
        target_type = '/'.join([i.src_portal_type for i in walkers])
        options = dict(target_type=target_type)
        clicked = request.form.has_key
        portal_url = getToolByName(context, 'portal_url')()
        if not haveContentMigrations:
            msg = _(u'Please install contentmigrations to be able to migrate to blobs.')
            IStatusMessage(request).addStatusMessage(msg, type='warning')
            options['nomigrations'] = 42
        elif clicked('migrate'):
            output = self.migrations()
            # Only count actual migration lines
            lines = output.split('\n')
            count = len([l for l in lines if l.startswith('Migrating')])
            msg = _(u'blob_migration_info',
                default=u'Blob migration performed for ${count} item(s).',
                mapping={'count': count})
            IStatusMessage(request).addStatusMessage(msg, type='info')
            options['count'] = count
            options['output'] = output
        elif clicked('cancel'):
            msg = _(u'Blob migration cancelled.')
            IStatusMessage(request).addStatusMessage(msg, type='info')
            request.RESPONSE.redirect(portal_url)
        else:
            li = list()
            for walker in walkers:
                li.extend(list( walker.walk()))
            options['available'] = len(li)
        return self.index(**options)
    
    def migrations(self):
        out = ''
        for walker in self.walkers():
            out += migrate(self, walker=lambda x: walker)
        return out
    
    def walkers(self):
        return [getMigrationWalker(self, migrator=ArticleMediaToBlobImageMigrator),
                getMigrationWalker(self, migrator=ArticleAudioToBlobMigrator) ]
    
    
    
    