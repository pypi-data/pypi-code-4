#####################################################################
# zopyx.authoring
# (C) 2010, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

import os
import hashlib
import zipfile
import tempfile

from Products.Five.browser import BrowserView

from zopyx.smartprintng.plone.resources import resources_registry
from zopyx.authoring.logger import LOG

EXT2TYPE = {
    '.pt' : 'AuthoringMasterTemplate',
    '.cover' : 'AuthoringCoverPage', 
    '.styles' : 'AuthoringStylesheet',
    '.css': 'AuthoringStylesheet',
    '.jpg' : 'AuthoringImageResource', 
    '.png' : 'AuthoringImageResource', 
    '.gif' : 'AuthoringImageResource', 
    '.hyp' : 'AuthoringBinaryResource', 
    '.otf' : 'AuthoringBinaryResource', 
    '.ttf' : 'AuthoringBinaryResource', 
    '.calibre' : 'AuthoringCalibreProfile', 
}

class AuthoringTemplateView(BrowserView):

    def __init__(self, context, request):
        self.request = request
        self.context = context

    def available_resources(self):
        """ Return all registred resources from SmartPrintNG """
        return sorted(resources_registry.keys())

    def export_resource(self):
        """ Export all data belong to a template as ZIP """

        zip_filename = tempfile.mktemp()
        ZIP = zipfile.ZipFile(zip_filename, 'w')
        for obj in self.context.getFolderContents():
            obj = obj.getObject()
            ZIP.writestr(obj.getId(), obj.get_data())

        ZIP.close()
        data = file(zip_filename).read()
        os.unlink(zip_filename) 
        R = self.request.RESPONSE
        R.setHeader('content-type', 'application/zip')
        R.setHeader('content-length', len(data))
        R.setHeader('content-disposition', 'attachment; filename="%s.zip"' % self.context.getId())
        R.write(data)

    def import_resource(self, resource, import_mode=''):
        """ Import a SmartPrintNG resource into the AuthoringTemplate """

        if import_mode == 'clear':
            self.context.manage_delObjects(self.context.objectIds())

        for dirname, dirnames, filenames in os.walk(resources_registry[resource]):
            if  '.svn' in dirname:
                continue

            for filename in filenames:
                fullname = os.path.join(dirname, filename)
                
                if not os.path.isfile(fullname):
                    continue
                basename, ext = os.path.splitext(fullname)

                # skip unsupported extensions 
                if not ext in EXT2TYPE.keys():
                    LOG.warn('Ignored during resource import: %s' % fullname)
                    continue

                if import_mode == 'incremental' and filename in self.context.objectIds():
                    self.context.manage_delObjects(filename)

                portal_type = EXT2TYPE.get(ext)
                self.context.invokeFactory(portal_type, id=filename, title=filename)
                self.context[filename].update_data(file(fullname).read())

                
        self.context.plone_utils.addPortalMessage(u'Resource %s imported' % resource)
        self.request.response.redirect(self.context.absolute_url())

    def sync(self, redirect=True):
        """ Sync filesystem-based resource directory with AuthoringTemplate in Plone
            (always sync from filesystem -> Plone)
        """

        resource = self.context.getResourceOnFilesystem()
        if not resource:
            if redirect:
                self.context.plone_utils.addPortalMessage(u'Nothing to be synced')
                self.request.response.redirect(self.context.absolute_url())
            return

        filenames_used = set()
        resource_dir = resources_registry.get(resource)
        if not resource_dir:
            raise RuntimeError('No configured resource "%s" found' % resource)

        for dirname, dirnames, filenames in os.walk(resource_dir):
            
            if  '.svn' in dirname:
                continue

            for filename in filenames:
                fullname = os.path.join(dirname, filename)
                if not os.path.isfile(fullname):
                    continue
                basename, ext = os.path.splitext(fullname)

                # skip unsupported extensions 
                if not ext in EXT2TYPE.keys():
                    LOG.warn('Ignored during resource import: %s' % fullname)
                    continue

                # compare md5 hashes 
                if filename in self.context.objectIds():
                    obj = self.context[filename]
                    fs_digest = hashlib.md5(file(fullname, 'rb').read()).hexdigest()
                    data = obj.get_data()
                    data_digest = hashlib.md5(data).hexdigest()
                    # hashes are the same -> nothing to do
                    if data_digest == fs_digest:
                        filenames_used.add(filename)
                        continue

                # object does not exist or hashes are different -> reimport/recreate
                LOG.info('Syncing %s:%s' % (resource, basename))
                filenames_used.add(filename)
                if filename in self.context.objectIds():
                    self.context.manage_delObjects(filename)

                portal_type = EXT2TYPE.get(ext)
                self.context.invokeFactory(portal_type, id=filename, title=filename)
                self.context[filename].update_data(file(fullname).read())

        # remove obsolete stuff
        existing_ids = set(self.context.contentIds())
        obsolete_ids = existing_ids - filenames_used
        self.context.manage_delObjects(list(obsolete_ids))

        if redirect:
            self.context.plone_utils.addPortalMessage(u'Synced %s from filesystem into template' % resource)
            self.request.response.redirect(self.context.absolute_url())
