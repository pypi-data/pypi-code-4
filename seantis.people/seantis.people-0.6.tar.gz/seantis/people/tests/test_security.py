from plone.supermodel import loadString

from seantis.people.supermodel import security
from seantis.people import tests


class TestSecurity(tests.IntegrationTestCase):

    def test_read_permissions(self):
        model = loadString("""
            <model xmlns="http://namespaces.plone.org/supermodel/schema">
                <schema />
            </model>
        """)

        security.set_read_permissions(
            model.schema, {'fieldname': 'zope2.View'}
        )
        self.assertEqual(security.get_read_permissions(model.schema), {
            'fieldname': 'zope2.View'
        })

    def test_had_read_access(self):
        model = loadString("""
            <model xmlns="http://namespaces.plone.org/supermodel/schema">
                <schema />
            </model>
        """)

        context = self.new_temporary_folder()

        # no permission -> has access
        self.assertTrue(
            security.has_read_access(model.schema, 'fieldname', context)
        )

        security.set_read_permissions(
            model.schema, {'fieldname': 'cmf.ManagePortal'}
        )

        # anonymous has no access now
        self.assertFalse(
            security.has_read_access(model.schema, 'fieldname', context)
        )

        # but the admin does
        with self.user('admin'):
            self.assertTrue(
                security.has_read_access(model.schema, 'fieldname', context)
            )
