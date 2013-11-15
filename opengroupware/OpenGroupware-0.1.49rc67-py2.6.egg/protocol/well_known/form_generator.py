#
# Copyright (c) 2013
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
import json
import yaml
from datetime import datetime
from coils.core import \
    NotImplementedException, \
    NoSuchPathException, \
    BLOBManager, \
    InsufficientParametersException, \
    CoilsException, \
    get_yaml_struct_from_project7000
from coils.net import Protocol, PathObject
from namedpathobject import NamedPathObject
from utility import get_object_from_project7000_path
from orm_attributes import ORM_ATTRIBUTES

'''
curl -u ogo:fred123 'http://127.0.0.1:8080/.well-known/opengroupware/
    ormgenerator.yaml?entity=Task&kind=TEST_KIND1'
'''


class FormGenerator(NamedPathObject):

    def __init__(self, parent, name, **params):
        NamedPathObject.__init__(self, parent, name, **params)

    def _encode(self, o):
        if (isinstance(o, datetime)):
            return  o.strftime('%Y-%m-%dT%H:%M:%S')
        raise TypeError()

    def do_GET(self):

        result = None

        if 'entity' not in self.parameters:
            raise InsufficientParametersException(
                '"entity" [string] is a required parameter; specify a '
                'valid Omphalos entity name.')

        if 'kind' not in self.parameters:
            raise InsufficientParametersException(
                '"kind" [string] is a required parameter; specify a '
                'defined Kind (TKO) value.')

        entity_name = self.parameters['entity'][0]
        if entity_name == 'File':
            entity_name == 'Document'

        entity_kind = self.parameters['kind'][0]

        # Load the defined kinds file
        try:
            defined_kinds = \
                get_yaml_struct_from_project7000(
                    context=self.context,
                    path='/DefinedKinds.yaml',
                    access_check=False, )
        except:
            raise NoSuchPathException(
                'The defined properties document in Project 7000 '
                '(/DefinedKinds.yaml) has not been provisioned')

        if entity_name not in defined_kinds:
            raise NoSuchPathException(
                '"{0}" is not an entity with defined kinds'.
                format(entity_name, ))

        if entity_kind not in defined_kinds[entity_name]:
            raise NoSuchPathException(
                'Kind "{0}" is not defined for entity "{1}"'.
                format(entity_kind, entity_name, ))

        kind_desc = defined_kinds[entity_name][entity_kind]
        kind_desc['properties'] = []
        if entity_name in ORM_ATTRIBUTES:
            kind_desc['attributes'] = ORM_ATTRIBUTES[entity_name]
        else:
            kind_desc['attributes'] = []

        # Load the defined properties file
        try:
            defined_properties = \
                get_yaml_struct_from_project7000(
                    context=self.context,
                    path='/DefinedProperties.yaml',
                    access_check=False, )
        except:
            raise NoSuchPathException(
                'The defined properties document in Project 7000 '
                '(/DefinedProperties.yaml) has not been provisioned')

        # expand kind with properties from DefinedProperties.yaml
        if entity_name in defined_properties:
            for prop_spec in defined_properties[entity_name]:
                if (
                    entity_kind.lower() in
                    [x.lower() for x in prop_spec['tags']]
                ):
                    kind_desc['properties'].append(prop_spec)

        result = kind_desc

        # Render result
        if result:

            if self.name.endswith('.json'):

                content_type = 'application/json'
                result = json.dumps(result, default=self._encode)

            elif self.name.endswith('.yaml'):

                content_type = 'application/yaml'
                result = yaml.dump(result)

            else:

                self.no_such_path()

            self.request.simple_response(
                200,
                data=result,
                mimetype=content_type, )

        else:

            raise CoilsException(
                'Unable to marshall handle to defined properties document; '
                'corrupted permissions?')
