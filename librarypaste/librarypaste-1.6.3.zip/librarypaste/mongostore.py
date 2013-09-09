import pymongo
import gridfs

from datastore import DataStore

class MongoDBDataStore(pymongo.Connection, DataStore):
    db_name = 'librarypaste'
    @property
    def db(self):
        return self[self.db_name]

    @classmethod
    def from_uri(cls, uri):
        store = cls(uri)
        uri_p = pymongo.uri_parser.parse_uri(uri)
        if uri_p['database']:
            store.db_name = uri_p['database']
        return store

    def _store(self, uid, content, data=None):
        """Store the given dict of content at uid. Nothing returned."""
        doc = dict(uid=uid)
        if data:
            gfs = gridfs.GridFS(self.db)
            id = gfs.put(data, encoding='utf-8')
            doc.update(data_id=id)
        doc.update(content)
        self.db.pastes.save(doc, w=1)

    def _storeLog(self, nick, time, uid):
        """Adds the nick & uid to the log for a given time/order. No return."""
        query = dict(uid=uid)
        update = {'$set': dict(nick=nick, time=time)}
        self.db.pastes.update(query, update)

    def _retrieve(self, uid):
        """Return a dict with the contents of the paste, including the raw
        data, if any, as the key 'data'. Must pass in uid, not shortid."""
        query = dict(uid=uid)
        doc = self.db.pastes.find_one(query)
        if 'data_id' in doc:
            data_id = doc.pop('data_id')
            gfs = gridfs.GridFS(self.db)
            doc.update(data = gfs.get(data_id).read())
        return doc

    def lookup(self, nick):
        """Looks for the most recent paste by a given nick.
        Returns the uid or None"""
        query = dict(nick=nick)
        order = dict(time=pymongo.DESCENDING)
        recs = self.db.pastes.find(query).order(order).limit(1)
        try:
            return next(recs)['uid']
        except StopIteration:
            pass

    def _lookupUid(self, shortid):
        query = dict(shortid=shortid)
        rec = self.db.pastes.find_one(query)
        return rec['uid']

    def list(self):
        return (doc['uid'] for doc in self.db.pastes.find(fields=['uid']))
