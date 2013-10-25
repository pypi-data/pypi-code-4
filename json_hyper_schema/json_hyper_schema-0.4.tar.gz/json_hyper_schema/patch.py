from uuid import uuid4 as uuid
from json_patch import Patch


class SchemaPatch(Patch):
    def __init__(self, schema, data):
        self.schema = schema

        super(SchemaPatch, self).__init__([])

        for func_name in [name for name in dir(self) if name.startswith('_patch_')]:
            operation = getattr(self, func_name)(data)
            if operation:
                self.append(operation)
    
    def _patch_default(self, data):
        if 'default' in self.schema and not data:
            return {'op': 'add', 'path': '/', 'value': self.schema['default']}

    def _patch_uuid(self):
        if 'uuid' in self.schema:
            return {'op': 'add', 'path': '/', 'value': uuid()}

        
            
                     
        
        
