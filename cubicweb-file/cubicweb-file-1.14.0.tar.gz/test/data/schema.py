from yams.buildobjs import RelationDefinition
from cubes.folder.schema import Folder

# XXX dirty hack to be quite sure tests won't fail due to path being >
# 64 chars
Folder.get_relation('name').constraints[0].max = 256
class filed_under(RelationDefinition):
    subject = 'File'
    object = 'Folder'

