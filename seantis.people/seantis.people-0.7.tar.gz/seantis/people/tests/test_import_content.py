from textwrap import dedent

from zope import schema
from plone.supermodel import loadString

from seantis.people import tests
from seantis.people import interfaces
from seantis.people.errors import ContentImportError
from seantis.people.content.import_content import (
    get_dataset,
    get_attribute_map,
    get_attribute_values,
    import_people,
    validate_attribute_values
)


class TestImportContent(tests.IntegrationTestCase):

    def test_import_people_csv(self):
        folder = self.new_temporary_folder()
        model = """<?xml version='1.0' encoding='utf8'?>
        <model  xmlns="http://namespaces.plone.org/supermodel/schema"
                xmlns:people="http://namespaces.plone.org/supermodel/people">
            <schema>
                <people:title>
                    <people:item>firstname</people:item>
                </people:title>
                <field name="firstname" type="zope.schema.TextLine">
                    <title>First Name</title>
                </field>
                <field name="lastname" type="zope.schema.TextLine">
                    <title>Last Name</title>
                </field>
            </schema>
        </model>"""

        portal_type = self.new_temporary_type(
            model_source=model,
            behaviors=[interfaces.INameFromPerson.__identifier__],
        ).id

        with self.user('admin'):
            import_people(self.request, folder, portal_type, 'csv', dedent("""
                First Name,Last Name,Town
                Peter,Griffin,Quahog
                Glenn,Quagmire,Quahog
            """.lstrip('\n')))

        self.assertEqual(folder['peter'].firstname, 'Peter')
        self.assertEqual(folder['peter'].lastname, 'Griffin')
        self.assertEqual(folder['glenn'].firstname, 'Glenn')
        self.assertEqual(folder['glenn'].lastname, 'Quagmire')

        # no town in the schema
        self.assertFalse(hasattr(folder['peter'], 'town'))
        self.assertFalse(hasattr(folder['glenn'], 'town'))

    def test_import_people_error_in_row(self):
        folder = self.new_temporary_folder()
        model = """<?xml version='1.0' encoding='utf8'?>
        <model  xmlns="http://namespaces.plone.org/supermodel/schema"
                xmlns:people="http://namespaces.plone.org/supermodel/people">
            <schema>
                <people:title>
                    <people:item>name</people:item>
                </people:title>
                <field name="name" type="zope.schema.TextLine">
                    <title>Name</title>
                </field>
                <field name="age" type="zope.schema.Int">
                    <title>Age</title>
                </field>
            </schema>
        </model>"""

        portal_type = self.new_temporary_type(
            model_source=model,
            behaviors=[interfaces.INameFromPerson.__identifier__],
        ).id

        self.login('admin')

        # error with a column avaiable
        try:
            import_people(self.request, folder, portal_type, 'csv', dedent("""
                Name,Age
                Macallan,15
                Glenmorangie,Sixteen
            """.lstrip('\n')))
        except ContentImportError, e:
            self.assertIn('invalid literal for int', e.message)
            self.assertEqual(e.rownumber, 2)
            self.assertEqual(e.colname, 'Age')
        else:
            assert False, "The exception should have occurred."

        # error without column available
        try:
            # no folder is given
            import_people(self.request, None, portal_type, 'csv', dedent("""
                Name,Age
                Macallan,15
            """.lstrip('\n')))
        except ContentImportError, e:
            self.assertIn('Missing required parameter', e.message)
            self.assertEqual(e.rownumber, 1)
            self.assertEqual(e.colname, None)
        else:
            assert False, "The exception should have occurred."

    def test_import_people_schema_validation(self):
        model = loadString("""<?xml version='1.0' encoding='utf8'?>
        <model  xmlns="http://namespaces.plone.org/supermodel/schema"
                xmlns:people="http://namespaces.plone.org/supermodel/people">
            <schema>
                <people:title>
                    <people:item>name</people:item>
                </people:title>
                <field name="name" type="zope.schema.TextLine">
                    <title>Name</title>
                </field>
                <field name="age" type="zope.schema.Int" required="false">
                    <title>Age</title>
                    <required>False</required>
                </field>
            </schema>
        </model>""")

        try:
            validate_attribute_values(model.schema, {'age': 1})
        except ContentImportError, e:
            self.assertIs(type(e), ContentImportError)
            self.assertEqual(e.colname, u'Name')
            self.assertEqual('Required column is missing', e.message)
        else:
            assert False, "The exception should have occurred."

        validate_attribute_values(model.schema, {'name': u'one', 'age': 1})

    def test_get_attribute_values(self):
        casts = [
            (schema.Text, u'Test', u'Test'),
            (schema.Int, u'1', 1),
            (schema.Bool, u'True', True),
            (schema.Bool, u'False', False),
            (schema.Bool, u'True', True),
            (schema.Bool, u'', False)
        ]
        for ix, (fieldtype, value, expected) in enumerate(casts):
            key = str(ix)

            record = {key: value}
            attrmap = {key: fieldtype(__name__=key)}

            result = get_attribute_values(record, attrmap)
            self.assertEqual(result[key], expected)

    def test_get_attribute_values_validation_error(self):
        record = {'test': u'www.example.com'}
        attrmap = {'test': schema.URI(__name__='test')}

        try:
            get_attribute_values(record, attrmap)
        except ContentImportError, e:
            self.assertEqual(e.colname, 'test')
            self.assertEqual(e.message, u'The specified URI is not valid.')
        else:
            assert False, "The exception should have occured."

    def test_get_csv_dataset(self):
        ds = get_dataset('csv', dedent("""
            First Name,Last Name,Town
            Peter,Griffin,Quahog
            Glenn,Quagmire,Quahog
        """.lstrip('\n')))

        self.assertEqual(ds.headers, ['First Name', 'Last Name', 'Town'])
        self.assertEqual(ds.dict[0], {
            'First Name': 'Peter',
            'Last Name': 'Griffin',
            'Town': 'Quahog'
        })
        self.assertEqual(ds.dict[1], {
            'First Name': 'Glenn',
            'Last Name': 'Quagmire',
            'Town': 'Quahog'
        })

    def test_get_attribute_map(self):
        model = """<?xml version='1.0' encoding='utf8'?>
        <model  xmlns="http://namespaces.plone.org/supermodel/schema">
            <schema>
                <field name="firstname" type="zope.schema.TextLine">
                    <title>First Name</title>
                </field>
                <field name="lastname" type="zope.schema.TextLine">
                    <title>Last Name</title>
                </field>
            </schema>
        </model>"""

        portal_type = self.new_temporary_type(model_source=model).id

        self.assertRaises(
            ContentImportError,
            get_attribute_map, self.request, [], portal_type
        )

        try:
            get_attribute_map(
                self.request, ['firstname', 'First Name'], portal_type
            )
        except ContentImportError, e:
            self.assertIn('column is specified more than once', e.message)
        else:
            assert False, "The exception should have occured."

        attrmap = get_attribute_map(
            self.request, ['firstname', 'lastname'], portal_type
        )

        self.assertEqual(len(attrmap), 2)
        self.assertEqual(attrmap['firstname'].__name__, 'firstname')
        self.assertEqual(attrmap['lastname'].__name__, 'lastname')

        attrmap = get_attribute_map(
            self.request, ['First Name', 'Last Name'], portal_type
        )

        self.assertEqual(len(attrmap), 2)
        self.assertEqual(attrmap['First Name'].__name__, 'firstname')
        self.assertEqual(attrmap['Last Name'].__name__, 'lastname')

        attrmap = get_attribute_map(self.request, ['foo', 'bar'], portal_type)
        self.assertEqual(len(attrmap), 0)
