import pymongo

from .base import BackendBase

import logging
log = logging.getLogger(__name__)


class MongoBackend(BackendBase):
    connection_uri = "mongodb://localhost"
    db_name = "test_denormalize"
    # TODO: catch connection errors

    # References to the connection and database objects after connecting
    connection = None
    db = None

    def __init__(self, name=None, db_name=None, connection_uri=None):
        super(MongoBackend, self).__init__(name=name)
        if db_name:
            self.db_name = db_name
        if connection_uri:
            self.connection_uri = connection_uri
        self.connect()

    def connect(self):
        self.connection = pymongo.Connection(self.connection_uri, safe=True)
        self.db = getattr(self.connection, self.db_name)

    def deleted(self, collection, doc_id):
        log.debug('deleted: %s %s', collection.name, doc_id)
        col = getattr(self.db, collection.name)
        col.remove({'_id': doc_id})

    def added(self, collection, doc_id, doc):
        log.debug('added: %s %s', collection.name, doc_id)
        col = getattr(self.db, collection.name)
        # Replace any existing document
        col.update({'_id': doc_id}, doc, upsert=True)

    def changed(self, collection, doc_id, doc):
        log.debug('changed: %s %s', collection.name, doc_id)
        col = getattr(self.db, collection.name)
        # We are not allowed to update _id
        if '_id' in doc:
            del doc['_id']
        # Only update the documents fields. We keep any other fields
        # added by other code intact, as long as they are set on the
        # document root.
        col.update({'_id': doc_id}, {'$set': doc}, upsert=True)

    def get_doc(self, collection, doc_id):
        col = getattr(self.db, collection.name)
        return col.find_one({'_id': doc_id})

