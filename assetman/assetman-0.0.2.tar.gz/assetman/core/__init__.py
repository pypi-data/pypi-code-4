# -*- coding: utf-8 -*-

from assetman.service import s3
from assetman.core import assets

class Assetman(object):

	def __init__(self, key, secret, bucket):
		self._aws_key = key
		self._aws_secret = secret
		self._bucket_name = bucket
		self._connection = None

	@property
	def connection(self):
		if not self._connection:
			self._connection = s3.get_connection(self._aws_key, self._aws_secret)
		return self._connection

	def save_asset(self, asset):
		bucket = s3.get_bucket(self._bucket_name, self.connection)
		s3.upload_string_data(bucket, asset.uuid, asset.data, asset.public, asset.mime_type, asset.meta_data)
		return asset

	def get_asset(self, uuid):
		bucket = s3.get_bucket(self._bucket_name, self.connection)
		key = s3.get_key(bucket, uuid)
		if not key:
			return None
		
		asset = assets.lookup_by_type(key.get_metadata('asset_type'))(key.get_contents_as_string(), uuid)
		asset.url = key.generate_url(120)
		asset.mime_type = key.content_type
		asset.meta_data = key.metadata
		return asset

	def delete_asset(self, uuid):
		bucket = s3.get_bucket(self._bucket_name, self.connection)
		s3.delete_key(bucket, uuid)