from json_hyper_schema import Schema
from json_pointer import Pointer


class ResourceNotFound(Exception):
    pass


class ForbiddenError(Exception):
    pass


class ResourceExists(Exception):
    pass


class NotMatchedError(Exception):
    pass


class ResourceMeta(type):
    def __new__(cls, *args, **kwargs):
        result = super(ResourceMeta, cls).__new__(cls, *args, **kwargs)
        
        try:
            result.__doc__ = result.schema['description']
        except (TypeError, KeyError), e:
            print e

        return result
    

class Resource(dict):
    schema = None
    __metaclass__ = ResourceMeta

    def validate(self):
        """
        Validate the instance against it's schema

        :params patch: If true also patch the instance with default values from the schema

        :raises TypeError: if the instance has no schema associated
        """
        if self.schema is None:
            raise TypeError('Trying to validate instance without a schema')

        self.schema.validate(self)

    def patch(self, patch):
        patch.apply(self)

    def __getitem__(self, key):
        if isinstance(key, Pointer):
            return key.get(self)
        else:
            return super(Resource, self).__getitem__(key)

    @property
    def url(self):
        """
        Url where the instance can be retrieved

        :returns: a string with the url where the instance can be retrieved.
        This is infered from the schema.

        :raises AttributeError: when no url can be inferred
        """
        try:
            return self.schema.links(
                self, rel='self', media_type='application/json'
            )[0]['href']
        except IndexError:
            # try again without media_type
            try:
                return self.schema.links(self, 'self')[0]['href']
            except IndexError:
                raise AttributeError('No self link defined for resource')


class StoredResourceMeta(ResourceMeta):
    def __new__(cls, *args, **kwargs):
        result = super(StoredResourceMeta, cls).__new__(cls, *args, **kwargs)
        
        if result.queryset and result.schema:
            result.objects = result.queryset(result)

        return result


class StoredResource(Resource):
    queryset = None

    __metaclass__ = StoredResourceMeta

    @classmethod
    def create(cls, data, validate=True, **kwargs):
        resource = cls(data)
        
        if validate:
            resource.validate()

        cls.objects.create(resource)
        
        return resource

    def save(self, validate=True, **kwargs):
        if validate:
            self.validate()

        self.objects.update(self, validate=validate)

    def delete(self, **kwargs):
        self.objects.delete(self)

    @property
    def exists(self):
        try:
            self.objects.get(self.url)
            return True
        except ResourceNotFound:
            return False
