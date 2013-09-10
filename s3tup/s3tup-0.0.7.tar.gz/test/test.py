import unittest
import os
import random
import string
import logging

from jinja2 import Environment, FileSystemLoader, Template
import boto

import secrets

import s3tup

template_path = os.path.join(os.path.dirname(__file__),'templates')
env = Environment(loader=FileSystemLoader(template_path))
env.globals['access_key_id'] = secrets.AWS_ACCESS_KEY_ID
env.globals['secret_access_key'] = secrets.AWS_SECRET_ACCESS_KEY
env.globals['owner_email'] = 'alex@heyimalex.com'
env.globals['owner_id'] = "35b2517484f1c7048553ffe3bd0356674d4fe528e7736a8dedcf66f88455ec60"

s3tup_log = logging.getLogger('s3tup')
s3tup_log.setLevel(logging.CRITICAL)

os.environ['AWS_ACCESS_KEY_ID'] = secrets.AWS_ACCESS_KEY_ID
os.environ['AWS_SECRET_ACCESS_KEY'] = secrets.AWS_SECRET_ACCESS_KEY

class MatcherTests(unittest.TestCase):

    def test_patterns(self):
        m = s3tup.utils.Matcher()
        m.patterns = ['*.py', '*.md']

        self.assertTrue(m.match('test.py'))
        self.assertTrue(m.match('test.md'))
        self.assertFalse(m.match('test.ps'))
        self.assertFalse(m.match('testpy'))

    def test_ignore_patterns(self):
        m = s3tup.utils.Matcher()

        m.ignore_patterns = ['*.py', '*.md']
        self.assertFalse(m.match('test.py'))
        self.assertFalse(m.match('test.md'))
        self.assertTrue(m.match('test.yml'))

    def test_regexes(self):
        pass

    def test_ignore_regexes(self):
        pass

class KeyConfiguratorTests(unittest.TestCase):

    def test_configure(self):
        # Create configurator
        c = s3tup.key.KeyConfigurator()
        c.reduced_redundancy = True
        c.encrypt = False
        c.cache_control = 'test'
        c.canned_acl = 'public-read'
        c.metadata = {'some':'metadata'}

        # Create new key and run configurator on it
        k = s3tup.key.Key(None, 'test', None, canned_acl='private',
                          encrypt=True, metadata={'some':'otherdata'})
        k = c.configure(k)

        # Confirm configurator worked as expected
        self.assertTrue(k.reduced_redundancy)
        self.assertFalse(k.encrypt)
        self.assertEqual(k.cache_control, 'test')
        self.assertEqual(k.canned_acl, 'public-read')
        self.assertEqual(k.metadata['some'], 'metadata')

    def test_effects_key(self):
        m = s3tup.utils.Matcher(['*.py',])
        c = s3tup.key.KeyConfigurator(matcher=m)
        self.assertTrue(c.effects_key('test.py'))
        self.assertFalse(c.effects_key('test.md'))

class KeyDiffTests(unittest.TestCase):
     def runTest(self):
        before = [
            {'name':'unmodified', 'etag':'a', 'size':1},
            {'name':'modified_md5', 'etag':'a', 'size':1},
            {'name':'modified_size', 'etag':'a', 'size':1},
            {'name':'modified_both', 'etag':'a', 'size':1},
            {'name':'removed', 'etag':'a', 'size':1},
        ]
        after = [
            {'name':'unmodified', 'etag':'a', 'size':1},
            {'name':'modified_md5', 'etag':'b', 'size':1},
            {'name':'modified_size', 'etag':'a', 'size':2},
            {'name':'modified_both', 'etag':'b', 'size':2},
            {'name':'new', 'etag':'a', 'size':1},
        ]
        out = s3tup.utils.key_diff(before, after)

        self.assertIn('unmodified', out['unmodified'])
        self.assertIn('modified_md5', out['modified'])
        self.assertIn('modified_size', out['modified'])
        self.assertIn('modified_both', out['modified'])
        self.assertIn('removed', out['removed'])
        self.assertIn('new', out['new'])

        self.assertEqual(len(out['unmodified']), 1)
        self.assertEqual(len(out['modified']), 3)
        self.assertEqual(len(out['new']), 1)
        self.assertEqual(len(out['removed']), 1)

class KeyFactoryTests(unittest.TestCase):
    pass

class KeyTests(unittest.TestCase):

    def test_invalid_kwarg_in_constructor(self):
        with self.assertRaises(TypeError):
            s3tup.key.Key(None, None, None, invalid_kwarg=True)

    def test_constructor(self):
        s3tup.key.Key(None, None, None, acl='', cache_control='',
                      canned_acl='', content_disposition='',
                      content_encoding='', content_type='',
                      content_language='', encrypt=True, expires='',
                      metadata={'test':'val'}, reduced_redundancy=True)

    def test_constructor_defaults(self):
        k = s3tup.key.Key(None, None, None)
        self.assertFalse(k.reduced_redundancy)
        self.assertFalse(k.encrypt)
        self.assertEqual(k.metadata, {})
        with self.assertRaises(AttributeError):
            k.canned_acl

class MakeBucketTests(unittest.TestCase):
    def test_kwarg_conn(self):
        conn = s3tup.connection.Connection('custom', 'custom')
        b = s3tup.bucket.make_bucket(conn=conn, bucket='test',
                                    access_key_id='kwarg',
                                    secret_access_key='kwarg')
        self.assertEqual(b.conn.access_key_id, 'kwarg')
        self.assertEqual(b.conn.secret_access_key, 'kwarg')        

    def test_param_conn(self):
        conn = s3tup.connection.Connection('param', 'param')
        b = s3tup.bucket.make_bucket(conn=conn, bucket='test')
        self.assertEqual(b.conn.access_key_id, 'param')
        self.assertEqual(b.conn.secret_access_key, 'param')

    def test_none_conn(self):
        b = s3tup.bucket.make_bucket(conn=None, bucket='test')
        self.assertEqual(b.conn.access_key_id, secrets.AWS_ACCESS_KEY_ID)
        self.assertEqual(b.conn.secret_access_key,
                         secrets.AWS_SECRET_ACCESS_KEY)

    def test_key_factory_creation(self):
        pass

class KeyTests(unittest.TestCase):
    pass

class BucketTests(unittest.TestCase):
    def setUp(self):
        # Create a random bucket name
        bucket_name = 's3tup-testing.'
        for x in range(25):
            bucket_name +=random.choice(string.ascii_lowercase+string.digits)
        self.bucket_name = bucket_name

        # Create the bucket using boto
        self.s3 = boto.connect_s3()
        self.boto_bucket = self.s3.create_bucket(self.bucket_name)

        # Create the s3tup bucket we'll testing on
        conn = s3tup.connection.Connection()
        self.s3tup_bucket = s3tup.bucket.Bucket(conn, self.bucket_name)

    def tearDown(self):
        self.s3.delete_bucket(self.bucket_name)

    def test_acl(self):
        before = self.boto_bucket.get_acl().to_xml()
        b = self.s3tup_bucket

        # TODO: Actually set different acl
        b.acl = env.get_template('acl.xml').render()
        b.sync()
        after = self.boto_bucket.get_acl().to_xml()
        self.assertEqual(after, before)

        # Restore default bucket config
        b.acl = None
        b.sync()
        after = self.boto_bucket.get_acl().to_xml()
        self.assertEqual(before, after)

        b.acl = "invalid acl"
        with self.assertRaises(s3tup.exception.S3Error):
            b.sync()

    def test_cors(self):
        pass

    def test_policy(self):
        pass

    def test_logging(self):
        pass

    def test_versioning(self):
        pass

    def test_website(self):
        pass

    def test_region(self):
        # Boto has already created the bucket by this point...
        # So we'll just test that it raises an exception
        b = self.s3tup_bucket
        b.region = 'ap-southeast-2'
        with self.assertRaises(s3tup.exception.S3Error):
            b.sync()

        # No region is set
        b.region = ''
        b.sync()
        b.region = None
        b.sync()

    def test_canned_acl(self):
        #b = self.s3tup_bucket
        #b.canned_acl = 'public-read-write'
        #b.sync()
        # To be continued...
        pass

    def test_tagging(self):
        b = self.s3tup_bucket
        b.tagging = env.get_template('tagging.xml').render()
        b.sync()

        tags = self.boto_bucket.get_tags()

        # get_tags returns them backwards
        self.assertEqual(tags[0][1].key, 'tag1')
        self.assertEqual(tags[0][1].value, 'val1')
        self.assertEqual(tags[0][0].key, 'tag2')
        self.assertEqual(tags[0][0].value, 'val2')

        b.tagging = None
        b.sync()

        with self.assertRaises(boto.exception.S3ResponseError):
            self.boto_bucket.get_tags()

class RsyncTests(unittest.TestCase):
    def setUp(self):
        s3 = boto.connect_s3()
        pass
        # Create bucket mock

class IntegrationTests(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()