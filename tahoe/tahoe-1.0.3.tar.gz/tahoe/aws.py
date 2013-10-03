"""
The MIT License (MIT)

Copyright (c) 2013 Lunar Technology Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import urlparse

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.exception import S3ResponseError


class S3Bucket(object):
    def __init__(self, bucket):
        """
        Accepts a boto `Bucket` instance.
        """
        self.bucket = bucket

    @property
    def name(self):
        """
        The name of this bucket.
        """
        return self.bucket.name

    def clear(self):
        # NOOP
        pass

    def get_url_for(self, key, ttl=None):
        k = Key(self.bucket)
        k.key = key
        if ttl:
            return k.generate_url(expires_in=self.url_ttl)
        return k.generate_url()

    def list(self, prefix=''):
        """
        The contents of this bucket.
        """
        keys = self.bucket.list(prefix=prefix)
        return [key.name for key in keys]

    def get_key(self, key):
        """
        Returns the value found at key.
        """
        k = Key(self.bucket)
        k.key = key
        try:
            data = k.get_contents_as_string()
        except S3ResponseError:
            data = None
        return data

    def set_key(self, key, value, replace=True):
        """
        Applies the value to the given key.
        """
        k = Key(self.bucket)
        k.key = key
        return k.set_contents_from_string(value, replace=replace)

    def copy(self, src_key, dst_bucket, dst_key, metadata=None):
        """
        - `src_key`: A string of where the data exists in the source bucket
        - `dst_bucket`: An `S3Bucket` instance where the key should be copied
                        to.
        - `dst_key`: A string of where the data should exist in the
                     destination bucket.
        - `metadata`: Metadata to be associated with new key. If metadata is
                      supplied, it will replace the metadata of the source
                      key being copied. If no metadata is supplied, the
                      source key's metadata will be copied to the new key.
        """
        s_key = Key(self.bucket)
        s_key.key = src_key
        s_key.copy(dst_bucket.name, dst_key, metadata=metadata)


class MockS3Bucket(object):
    def __init__(self, name):
        self.store = {}
        self.host = "testing.s3.amazonaws.com"
        self.name = name

    def clear(self):
        self.store = {}

    def get_url_for(self, key):
        return urlparse.urljoin("http://{}".format(self.host), key)

    def list(self, prefix=''):
        if not prefix:
            return self.store.keys()
        else:
            return [k for k in self.store.keys() if k.startswith(prefix)]

    def get_key(self, key):
        return self.store.get(key)

    def set_key(self, key, value):
        self.store[key] = value

    def copy(self, src_key, dst_bucket, dst_key, metadata=None):
        s_key_value = self.get_key(src_key)
        if s_key_value:
            dst_bucket.set_key(dst_key, s_key_value)


class AWS(object):
    def __init__(self, config):
        self.config = config
        self.aws_key_id = self.config.get('AWS_ACCESS_KEY_ID')
        self.aws_key_secret = self.config.get('AWS_ACCESS_KEY_SECRET')
        self._s3_connection = None
        self._s3_buckets = {}
        self.testing = self.config.get('TESTING', False)

    @property
    def s3_connection(self):
        if not self._s3_connection:
            self._s3_connection = self._get_s3_connection()
        return self._s3_connection

    def _get_s3_connection(self):
        return S3Connection(self.aws_key_id, self.aws_key_secret)

    def clear_mock_buckets(self):
        if self.testing:
            for bucket in self._s3_buckets.values():
                bucket.clear()

    def get_bucket(self, bucket_name):
        bucket = self._s3_buckets.get(bucket_name)
        if not bucket:
            if self.testing:
                bucket = MockS3Bucket(name=bucket_name)
            else:
                bucket = S3Bucket(
                    bucket=self.s3_connection.get_bucket(bucket_name)
                    )
            self._s3_buckets[bucket_name] = bucket
        return bucket
