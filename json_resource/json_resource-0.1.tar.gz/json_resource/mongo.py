import re
import pymongo

from json_resource import QuerySet, StoredResource, ResourceNotFound, \
    ResourceExists


class MongoQuerySet(QuerySet):
    def __init__(self, resource):
        super(MongoQuerySet, self).__init__(resource)

        self._result = None

        self.ensure_indexes()

    def ensure_indexes(self):
        for link in self.resource.schema['links']:
            args = re.findall("\{(\w*)\}", link['href'])
            self.collection.ensure_index(
                [(arg, pymongo.ASCENDING) for arg in
                 args]
            )
            
        for index in self.resource.schema.get('indexes', []):
            self.collection.ensure_index(
                [(field, pymongo.ASCENDING) for field in index]
            )

    @property
    def collection(self):
        return self.resource.db[self.resource.schema['id']]

    @property
    def _fields(self):
        fields = dict((field, False) for field in self._exclude)
        fields['_id'] = False

        return fields

    @property
    def _cursor(self):
        if not self._result:
            self._result = self.collection.find(self._filter, self._fields)
            
            if self._limit:
                self._result.limit(self._limit)

            if self._offset:
                self._result.skip(self._offset)

        return self._result

    def __len__(self):
        return min(
            self._cursor.count() - self._offset,
            self._limit
        )
    
    def get(self, url):
        data = self.collection.find_one(
            {'_id': url},
            self._fields
        )

        if not data:
            raise ResourceNotFound()
        
        return self.resource(data)

    def delete(self, resource):
        result = self.collection.remove(
            {'_id': resource.url}
        )

        if result['n'] == 0:
            raise ResourceNotFound()

    def create(self, resource):
        resource['_id'] = resource.url

        try:
            self.collection.insert(
                resource
            )
        except pymongo.errors.DuplicateKeyError:
            raise ResourceExists(resource.url)
        
        del resource['_id']


class MongoResource(StoredResource):
    db = None
    host = '127.0.0.1'

    queryset = MongoQuerySet
