# -*- coding: utf-8 -*-

from boto.s3.connection import S3Connection
from boto.s3.key import Key

def get_connection(key, secret):
	connection = S3Connection(key, secret)
	return connection

def get_bucket(bucket_name, connection):
	bucket = connection.get_bucket(bucket_name)
	return bucket

def upload_string_data(bucket, path, string_data, public=False, mime_type=None, metadata=None):
	key = Key(bucket, path)
	if mime_type:
		key.content_type = mime_type
	if metadata:
		key.update_metadata(metadata)
	key.set_contents_from_string(string_data)
	if public:
		key.make_public()

def delete_key(bucket, path):
	key = bucket.get_key(path)
	if key:
		key.delete()

def get_key(bucket, path):
	key = bucket.get_key(path)
	return key

def get_string_data(bucket, path):
	key = bucket.get_key(path)
	if key:
		return key.get_contents_as_string()