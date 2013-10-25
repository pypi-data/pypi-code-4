import re
import urllib
from urlparse import urlparse, parse_qs

import pymongo

from json_schema import Schema

from json_instance import JSONObject


DEFAULT_LIMIT = 10


class ResourceNotFound(Exception):
    pass


class InvalidResourceVersion(Exception):
    pass


class AuthorizationRequired(Exception):
    pass


class StoredObjectMeta(JSONObject.__metaclass__):
    def __new__(cls, *args, **kwargs):
        result = super(StoredObjectMeta, cls).__new__(cls, *args, **kwargs)

        if isinstance(result._queryset, type):
            result.objects = result._queryset(result)

        return result


class StoredObject(JSONObject):
    _queryset = None

    __metaclass__ = StoredObjectMeta
    schema = Schema({})


    @property
    def exists(self, version=None):
        try:
            self.objects.get(self.url, version)
            return True
        except (TypeError, AttributeError, ResourceNotFound):
            return False

    def save(self, create=False, version=None, **kwargs):
        self.objects.save(self, create, version=version, **kwargs)

    def delete(self, version=None):
        self.objects.delete(self.url, version=version)

    def related(self, rel):
        regex = re.compile('\{\w+\}')

        href = regex.sub('*', self.schema.links[rel]['href'])
        registry =  dict(
            [(
                    regex.sub('*', value.schema.links['self']['href']), 
                    value) 
             for key, value in self._registry.items()])

        return registry[href].find(self.links[rel])

    @property
    def parent(self):
        if 'parent' in self.schema.links:
            return self.related('parent')
        elif 'instances' in self.schema.links:
            return self.related('instances')

    @property
    def parents(self):
        parent = self.parent

        if parent is not None:
            return parent.parents + [parent]
        else:
            return []


class StoredObjectListMeta(JSONObject.__metaclass__):
    def __new__(cls, name, bases, dct):

        if 'resource' in dct and dct['resource']:
            rel = dct.get('rel', StoredObjectList.rel)
            link = dct['resource'].schema.links[rel]

            schema = {
                'id': '%s-%s' % (dct['resource'].schema['id'], rel),
                'description': 'A list of %s objects' % dct['resource'].schema['id'],
                'properties': {
                    'found': {'type': 'number'},
                    'limit': {'type': 'number', 'default': DEFAULT_LIMIT},
                    'offset': {'type': 'integer', 'default': 0},
                    dct.get('instance_key', 'instances'): {
                        'items': dct['resource'].schema
                        }
                    },
                'links': [
                    {
                        'rel': 'self',
                        'href': link['href'],
                        'method': 'GET'
                        }
                    ]
                }

            for arg in link['args']:
                schema['properties'][arg] = \
                    dct['resource'].schema['properties'][arg]

            dct['schema'] = Schema(schema)

        result = super(StoredObjectListMeta, cls).__new__(
            cls,
            name,
            bases,
            dct
            )

        return result


class StoredObjectList(JSONObject):
    __metaclass__ = StoredObjectListMeta

    resource = None
    rel = 'instances'

    @classmethod
    def find(cls, url):
        url = urlparse(url)
        path = urllib.unquote(url.path)
        args = parse_qs(url.query)
        args = dict([(key, value[-1]) for key, value in args.items()])

        # get the filter from the url
        filter = {}
        link = cls.resource.schema.links[cls.rel]
        regex = re.compile(
            link['href'].replace('{', '(?P<').replace('}', r'>.+)')
            )

        filter = regex.match(path).groupdict()

        qs = cls.resource.objects.filter(filter)

        limit = args.get('limit', 10)
        offset = args.get('offset', 0)

        if hasattr(cls, 'fields'):
            qs.fields(cls.fields)

        result = {
            'found': len(qs),
            'limit': limit,
            'offset': offset,
            'instances': list(qs[offset:limit + offset])
            }

        result.update(filter)
        return cls(result)

    parent = StoredObject.parent
    parents = StoredObject.parents



