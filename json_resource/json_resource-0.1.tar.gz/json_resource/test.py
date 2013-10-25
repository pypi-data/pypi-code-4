import unittest
import mock

from pymongo import MongoClient

from json_resource import StoredResource, Resource, QuerySet, MongoResource, \
    ResourceNotFound, ResourceExists

from json_pointer import Pointer
from json_hyper_schema import Schema, ValidationError
from json_patch import Patch


schema = {
    'id': 'test',
    'description': 'Test Description',
    'title': 'Test Title',
    'properties': {
        'id': {'type': 'number', 'required': True},
        'type': {'type': 'string'}
    },
    'links': [
        {
            'rel': 'self',
            'mediaType': 'application/json',
            'href': '/test/{id}'
        },
        {
            'rel': 'self',
            'mediaType': 'application/jpeg',
            'href': '/test/{id}.jpg'
        }
    ]
}


class TestResource(Resource):
    schema = Schema(schema)


class ResourceTest(unittest.TestCase):
    def setUp(self):
        self.resource = TestResource({'id': 'bla'})

    def test_url(self):
        url = self.resource.url
        self.assertEqual(url, '/test/bla')

    def test_url_no_media_type(self):
        class NoMediaTypeResource(Resource):
            schema = Schema({
                'links': [{
                    'rel': 'self',
                    'href': '/'
                }]
            })
        url = NoMediaTypeResource({}).url
        self.assertEqual(url, '/')

    def test_url_missing(self):
        class EmptyResource(Resource):
            schema = Schema({
            })
            
        try:
            EmptyResource({}).url
        except AttributeError:
            pass

    def test_doc_string(self):
        self.assertEqual(self.resource.__class__.__doc__, 'Test Description')

    def test_get_item(self):
        self.assertEqual(
            self.resource[Pointer('/id')],
            'bla'
        )
        
        self.assertEqual(
            self.resource['id'],
            'bla'
        )

    def test_validate(self):
        self.assertRaises(
            ValidationError,
            self.resource.validate
        )

    def test_validate_no_schema(self):
        class NoSchemaResource(Resource):
            pass

        resource = NoSchemaResource({'id': 'bla'})
        self.assertRaises(
            TypeError,
            resource.validate
        )
        
    def test_patch(self):
        patch = Patch([{'op': 'add', 'value': 'bla', 'path': '/type'}])
        self.resource.patch(patch)
        self.assertEqual(self.resource['type'], 'bla')


class StoredTestResource(StoredResource):
    queryset = QuerySet
    schema = Schema(schema)


class StoredResourceTest(unittest.TestCase):
    def setUp(self):
        self.resource = StoredTestResource({'id': 1})

    def test_object(self):
        self.assertTrue(hasattr(self.resource, 'objects'))
        self.assertTrue(isinstance(self.resource.objects, QuerySet))

    def test_not_implemented(self):
        self.assertRaises(
            NotImplementedError, StoredTestResource.objects.create, {}
        )
        self.assertRaises(
            NotImplementedError, self.resource.objects.update, {}
        )
        self.assertRaises(
            NotImplementedError, self.resource.delete
        )
        
    @mock.patch.object(QuerySet, 'create')
    def test_create(self, create):
        resource = StoredTestResource.create({'id': 1})
        
        self.assertEqual(resource['id'], 1)

        create.assertCalledOnce()

    @mock.patch.object(QuerySet, 'create')
    def test_create_invalid(self, create):
        self.assertRaises(
            ValidationError,
            StoredTestResource.create,
            {'bli': 'bla'}
        )
        resource = StoredTestResource.create({'id': 'bla'}, validate=False)

        self.assertEqual(resource['id'], 'bla')
        create.assertCalledOnce()

    @mock.patch.object(QuerySet, 'update')
    def test_save(self, update):
        self.resource['id'] = 2
        self.resource.save()

        update.assertCalledOnce()

    @mock.patch.object(QuerySet, 'update')
    def test_save_invalid(self, update):
        self.resource['id'] = 'bla'

        self.assertRaises(
            ValidationError,
            self.resource.save
        )
        
        self.resource.save(validate=False)
        update.assertCalledOnce()

    @mock.patch.object(QuerySet, 'delete')
    def test_delete(self, delete):
        self.resource.delete(validate=False)
        delete.assertCalledOnce()


class MongoTestResource(MongoResource):
    schema = Schema(schema)
    db = MongoClient().test


class MongoResourceTest(unittest.TestCase):
    def tearDown(self):
        MongoClient().drop_database('test')

    def test_not_exists(self):
        resource = MongoTestResource({'id': 1})
        self.assertFalse(resource.exists)

    def test_create(self):
        self.assertEqual(len(MongoTestResource.objects), 0)
        resource = MongoTestResource.create({'id': 1})
        self.assertTrue(resource.exists)
        self.assertEqual(len(MongoTestResource.objects), 1)

    def test_create_duplicate(self):
        MongoTestResource.create({'id': 1})

        self.assertRaises(
            ResourceExists,
            MongoTestResource.create,
            {'id': 1}
        )

    def test_delete(self):
        resource = MongoTestResource.create({'id': 1})
        resource.delete()
        self.assertEqual(len(MongoTestResource.objects), 0)
        
        self.assertRaises(
            ResourceNotFound,
            resource.delete
        )
    
    def test_get(self):
        self.assertRaises(
            ResourceNotFound,
            MongoTestResource.objects.get,
            '/id/1'
        )
        resource = MongoTestResource.create({'id': 1})

        resource = MongoTestResource.objects.get(resource.url)
        self.assertEqual(resource['id'], 1)

    def test_iterate(self):
        MongoTestResource.create({'id': 1})
        
        for resource in MongoTestResource.objects:
            self.assertEqual(resource['id'], 1)
        
    def test_fields(self):
        resource = MongoTestResource.create({'id': 1, 'type': 'bla'})
        self.assertEqual(set(resource.keys()), set(['id', 'type']))

        resource = MongoTestResource.objects.exclude(['id']).get(resource.url)
        self.assertEqual(resource.keys(), ['type'])

    def test_filter(self):
        MongoTestResource.create({'id': 1, 'type': 'bla'})
        MongoTestResource.create({'id': 2, 'type': 'bla'})
        MongoTestResource.create({'id': 3, 'type': 'bli'})

        objects = MongoTestResource.objects.filter({'type': 'bla'})
        self.assertEqual(len(objects), 2)

        for resource in objects:
            self.assertEqual(resource['type'], 'bla')

        objects = MongoTestResource.objects.filter({'type': 'bli'})
        self.assertEqual(len(objects), 1)
            
    def test_getitem(self):
        MongoTestResource.create({'id': 1, 'type': 'bla'})
        MongoTestResource.create({'id': 2, 'type': 'bla'})
        MongoTestResource.create({'id': 3, 'type': 'bli'})
        
        resource = MongoTestResource.objects[0]
        self.assertTrue(resource['id'] in [1, 2, 3])

        self.assertEqual(len(MongoTestResource.objects[0:2]), 2)
        self.assertEqual(len(MongoTestResource.objects[1:2]), 1)
        
        self.assertRaises(
            IndexError, MongoTestResource.objects[:2].__getitem__, 3
        )

    def test_repr(self):
        self.assertTrue(MongoTestResource.objects.__repr__().find('[]') > 0)
        MongoTestResource.create({'id': 1, 'type': 'bla'})
        print MongoTestResource.objects.__repr__()
        self.assertTrue(MongoTestResource.objects.__repr__().find("'id': 1") > 0)
        MongoTestResource.create({'id': 2, 'type': 'bla'})
        self.assertTrue(MongoTestResource.objects.__repr__().find("'id': 2") > 0)
        MongoTestResource.create({'id': 3, 'type': 'bli'})
        self.assertTrue(MongoTestResource.objects.__repr__().find("...") > 0)
