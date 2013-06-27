import pytest
import pymongo

from . import DataStoreTest
from librarypaste import mongostore

class TestMongoDBDataStore(DataStoreTest):
	datastore = None

	@classmethod
	def setup_class(cls):
		try:
			cls.datastore = mongostore.MongoDBDataStore.from_uri(
				'mongodb://localhost/librarypaste-test')
		except pymongo.errors.AutoReconnect as e:
			pytest.skip("Local MongoDB not available ({msg})".format(
				msg = e))

	@classmethod
	def teardown_class(cls):
		if cls.datastore:
			cls.datastore.drop_database(cls.datastore.db_name)
