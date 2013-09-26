from yams.buildobjs import RelationDefinition
from yams.reader import context

if 'Folder' in context.defined:
    class filed_under(RelationDefinition):
        subject = 'VersionedFile'
        object = 'Folder'
