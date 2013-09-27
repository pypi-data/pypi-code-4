import mock
from django.test import SimpleTestCase

from zap.backends import LocalPostgresZap


class LocalPostgresZapTest(SimpleTestCase):

    def setUp(self):
        patch_getpwall = mock.patch('pwd.getpwall')
        patch_platform = mock.patch('zap.backends.postgresql.sys',
            new_callable=mock.PropertyMock)
        patch_debug = mock.patch('django.conf.settings.DEBUG',
            new_callable=mock.PropertyMock)

        self.patch_databases = mock.patch.dict('zap.backends.base.settings.DATABASES', {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'loldongs',
                'USER': 'loldongs',
                'PASSWORD': 'loldongs',
                'HOST': '',
                'PORT': '',
            },
        })


        self.mock_platform = patch_platform.start()
        self.mock_getpwall = patch_getpwall.start()
        self.mock_debug = patch_debug.start()

        self.mock_platform.return_value = 'linux2'
        self.mock_getpwall.return_value = [('root',),('postgres',),('foo',)]
        self.mock_debug = True

        self.addCleanup(patch_platform.stop)
        self.addCleanup(patch_getpwall.stop)
        self.addCleanup(self.patch_databases.stop)
        self.addCleanup(patch_debug.stop)

    def test_can_zap(self):
        zap = LocalPostgresZap()
        self.assertTrue(zap.can_zap())

    def test_cannot_zap_mac(self):
        zap = LocalPostgresZap()
        self.mock_platform.return_value = 'darwin'
        self.assertFalse(zap.can_zap())

    def test_cannot_zap_non_localhost(self):
        zap = LocalPostgresZap()
        self.patch_databases.values['default']['HOST'] = '127.0.0.1'
        self.assertTrue(zap.can_zap())
        self.patch_databases.values['default']['HOST'] = 'localhost'
        self.assertTrue(zap.can_zap())
        self.patch_databases.values['default']['HOST'] = ''
        self.assertTrue(zap.can_zap())
        self.patch_databases.values['default']['HOST'] = 'lolling-dongs-213.heroku.com'
        self.assertFalse(zap.can_zap())

    def test_cannot_zap_if_no_postgresql_user(self):
        zap = LocalPostgresZap()
        self.mock_getpwall.return_value = [('root',),('dennis',),('foo',)]
        self.assertFalse(zap.can_zap())

    def test_cannot_zap_if_not_postgres_engine(self):
        zap = LocalPostgresZap()
        self.patch_databases.values['default']['ENGINE'] = 'django.db.backends.sqlite3'
        self.assertFalse(zap.can_zap())
