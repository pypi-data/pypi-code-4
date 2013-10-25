import os
import unittest
import json

from json_reference import Reference

from json_hyper_schema import Schema, ValidationError

for filename in ['integer.json', 'subSchemas.json', 'folder/folderInteger.json']:
    with open(
        os.path.join(
            os.path.dirname(__file__),
            'tests/remote/%s' % filename
        ),
        'r'
    ) as data:
        Reference.register(
            'http://localhost:1234/%s' % filename,
            json.loads(data.read())
        )


class JSONPatchTestcase(object):
    def _test(self, data):
        schema = Schema(data['schema'])

        for test in data['tests']:
            if test['valid']:
                self.assertEqual(schema.validate(test['data']), None)
            else:
                self.assertRaises(
                    ValidationError,
                    schema.validate,
                    test['data']
                )

    def test(self):
        with open(
            os.path.join(
                os.path.dirname(__file__),
                'tests/%s' % self.filename
            ),
            'r'
        ) as json_file:
            tests = json.loads(json_file.read())
            
            for test in tests:
                self._test(test)
    

class TestAdditionalItems(JSONPatchTestcase, unittest.TestCase):
    filename = 'additionalItems.json'


class TestAdditionalProperties(JSONPatchTestcase, unittest.TestCase):
    filename = 'additionalProperties.json'


class TestDependencies(JSONPatchTestcase, unittest.TestCase):
    filename = 'dependencies.json'


class TestDisallow(JSONPatchTestcase, unittest.TestCase):
    filename = 'disallow.json'


class TestDivisibleBy(JSONPatchTestcase, unittest.TestCase):
    filename = 'divisibleBy.json'


class TestEnum(JSONPatchTestcase, unittest.TestCase):
    filename = 'enum.json'


class TestExtends(JSONPatchTestcase, unittest.TestCase):
    filename = 'extends.json'


class TestItems(JSONPatchTestcase, unittest.TestCase):
    filename = 'items.json'


class TestProperties(JSONPatchTestcase, unittest.TestCase):
    filename = 'properties.json'


class TestMaximum(JSONPatchTestcase, unittest.TestCase):
    filename = 'maximum.json'


class TestMaxItems(JSONPatchTestcase, unittest.TestCase):
    filename = 'maxItems.json'


class TestMaxLength(JSONPatchTestcase, unittest.TestCase):
    filename = 'maxLength.json'


class TestMinimum(JSONPatchTestcase, unittest.TestCase):
    filename = 'minimum.json'


class TestMinItems(JSONPatchTestcase, unittest.TestCase):
    filename = 'minItems.json'


class TestMinLength(JSONPatchTestcase, unittest.TestCase):
    filename = 'minLength.json'


class TestPattern(JSONPatchTestcase, unittest.TestCase):
    filename = 'pattern.json'


class TestPatternProperties(JSONPatchTestcase, unittest.TestCase):
    filename = 'patternProperties.json'


class TestRef(JSONPatchTestcase, unittest.TestCase):
    filename = 'ref.json'


class TestRefRemote(JSONPatchTestcase, unittest.TestCase):
    filename = 'refRemote.json'


class TestRequired(JSONPatchTestcase, unittest.TestCase):
    filename = 'required.json'


class TestType(JSONPatchTestcase, unittest.TestCase):
    filename = 'type.json'


class TestUniqueItems(JSONPatchTestcase, unittest.TestCase):
    filename = 'uniqueItems.json'


class TestBignum(JSONPatchTestcase, unittest.TestCase):
    filename = 'bignum.json'


class TestFormat(JSONPatchTestcase, unittest.TestCase):
    filename = 'format.json'


class TestErrorMessages(unittest.TestCase):
    def _validate(self, schema, data):
        Schema(schema).validate(data)

    def test_single(self):
        try:
            self._validate(
                {'type': 'number'},
                "string"
            )
        except ValidationError, e:
            self.assertTrue('/' in e.errors)
            self.assertEqual(len(e.errors['/']), 1)
            self.assertTrue('Not of type number' in e.errors['/'][0])
            self.assertTrue('Not of type number' in str(e.errors))
            self.assertTrue(isinstance(json.loads(str(e)), dict))
            

    def test_multiple(self):
        try:
            self._validate(
                {'type': 'string', 'format': 'email'},
                10
            )
        except ValidationError, e:
            self.assertTrue('/' in e.errors)
            self.assertEqual(len(e.errors['/']), 2)

    def test_properties(self):
        try:
            self._validate(
                {
                    'properties': {
                        'test': {
                            'type': 'string',
                            'format': 'email'
                        }
                    }
                },
                {'test': 10}
            )
        except ValidationError, e:
            self.assertTrue('/test/' in e.errors)
            self.assertEqual(len(e.errors['/test/']), 2)

    def test_items(self):
        try:
            self._validate(
                {
                    'items': {
                        'type': 'string',
                        'format': 'email'
                    }
                },
                [10]
            )
        except ValidationError, e:
            self.assertTrue('/0/' in e.errors)
            self.assertEqual(len(e.errors['/0/']), 2)

    def test_update_no_validation_error(self):
        error = ValidationError()
        self.assertRaises(
            TypeError,
            error.append,
            Exception()
        )


class TestLinks(unittest.TestCase):
    def test_links(self):
        schema = Schema({
            'links': [
                {'rel': 'self', 'href': '/{id}', 'schema': {}}
            ]
        })
        
        links = schema.links({'id': 'test', 'bla': 'bli'})

        self.assertEqual(links[0]['href'], '/test')
        self.assertTrue(isinstance(links[0]['schema'], Schema))

    def test_links_missing_data(self):
        schema = Schema({
            'links': [
                {'rel': 'self', 'href': '/{id}', 'schema': {}}
            ]
        })
        
        links = schema.links({})
        
        self.assertEqual(schema['links'][0]['href'], '/{id}')
        self.assertEqual(links[0]['href'], '/{id}')
        self.assertTrue(isinstance(links[0]['schema'], Schema))

    def test_links_filter(self):
        schema = Schema({
            'links': [
                {'rel': 'self', 'href': '/{id}', 'schema': {}},
                {'rel': 'other', 'href': '/{id}', 'schema': {}},
                {'rel': 'self', 'mediaType': 'application/jpeg',
                 'href': '/{id}', 'schema': {}}
            ]
        })
        
        links = schema.links({'id': 'test', 'bla': 'bli'}, rel='self')
        self.assertEqual(len(links), 2)

        links = schema.links({'id': 'test', 'bla': 'bli'}, rel='self',
                             media_type='application/jpeg')
        self.assertEqual(len(links), 1)


class TestExample(unittest.TestCase):
    def test_example(self):
        schema = Schema({
            'description': 'test schema',
            'properties': {
                'list': {
                    'items': {
                        'title': 'Test list',
                        'type': 'number',
                        'enum': [1, 2, 3]
                    }
                },
                'bli': {},
                'bla': {'type': 'string'},
                'test': {
                    'description': 'string item',
                    'type': 'string',
                    'format': 'email'
                }
            },
            'links': [
                {'rel': 'self', 'href': '/{id}', 'schema': {}}
            ]
        })

        self.assertTrue('test' in schema.example)
        
