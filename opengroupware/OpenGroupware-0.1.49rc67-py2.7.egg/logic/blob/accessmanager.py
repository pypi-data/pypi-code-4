#
# Copyright (c) 2010, 2012, 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
from coils.core import EntityAccessManager, ServerDefaultsManager


class BLOBEntityAccessManager(EntityAccessManager):

    __DebugOn__ = None

    def inherited_rights(self, entity, rights):
        for folder in entity.folder_entity_path:
            allowed = self.get_acls('allowed', folder)
            rights = rights.union(allowed)
            denied = self.get_acls('denied', folder)
            rights = rights.difference(denied)
        return rights

    def project_rights(self, entity, rights):
        if entity.project is None:
            return rights
        else:
            project_rights = \
                self._ctx.access_manager.access_rights(entity.project)
            if project_rights:
                rights = rights.union(project_rights)
        return rights

    @property
    def debug(self):
        return BLOBEntityAccessManager.__DebugOn__


class FolderAccessManager(BLOBEntityAccessManager):
    #TODO: Implement!
    __entity__ = 'Folder'

    def __init__(self, ctx):
        if (BLOBEntityAccessManager.__DebugOn__ is None):
            sd = ServerDefaultsManager()
            BLOBEntityAccessManager.__DebugOn__ = \
                sd.bool_for_default('OGoDocumentManagementDebugEnabled')
        EntityAccessManager.__init__(self, ctx)

    def implied_rights(self, objects):
        rights = {}
        for folder in objects:
            rights_set = self.project_rights(folder, set())
            rights[folder] = self.inherited_rights(folder, rights_set)
        if self.debug:
            for k, v in rights.items():
                self.log.debug('Implied rights for {0} are {1}'.format(k, v))
        return rights


class FileAccessManager(BLOBEntityAccessManager):
    '''
    Due to a stupid bug in early versions this access manager must register
    itself as procesing both "Document" and "File" entities.  All the Logic
    commands use the document:: domain, but the entity itself originally had
    a Coils entity name of "File"
    '''
    __entity__ = ['File', 'Document', 'Doc', ]

    def __init__(self, ctx):
        if (BLOBEntityAccessManager.__DebugOn__ is None):
            sd = ServerDefaultsManager()
            BLOBEntityAccessManager.__DebugOn__ = \
                sd.bool_for_default('OGoDocumentManagementDebugEnabled')
        EntityAccessManager.__init__(self, ctx)

    def implied_rights(self, objects):
        rights = {}
        for blob in objects:
            rights_set = self.project_rights(blob, set())
            rights[blob] = self.inherited_rights(blob, rights_set)
        if self.debug:
            for k, v in rights.items():
                self.log.debug('Implied rights for {0} are {1}'.format(k, v))
        return rights
