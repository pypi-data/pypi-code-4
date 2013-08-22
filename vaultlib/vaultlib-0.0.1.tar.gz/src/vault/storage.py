import pycouchdb
from .databag import Databag


class Storage(object):
    """
    A Databag vault on couchdb.
    """

    def __init__(self, protocol, host, port=5984, database='vault', verify=True):
        """
            protocol can be: http or https.
            verify=False (if https): ignore verifying the SSL certificate
        """
        server = pycouchdb.Server("%s://%s:%s" % (
            protocol,
            host,
            port
        ), verify=verify)
        self.db = server.database(database)
        self.mapFunc = \
            "function(doc) { emit(doc._id, {_id: doc._id, data: doc.data}); }"

    def add_databag(self, databag):
        if self.get_databag(databag._id):
            self.db.delete(databag._id)
        self.db.save(databag.__dict__)

    def get_databag(self, _id):
        try:
            result = self.db.get(_id)
            return Databag(result.get("_id"), result.get("data"))
        except pycouchdb.exceptions.NotFound:
            return None

    def delete_databag(self, _id):
        self.db.delete(_id)

    def list_databags(self, mapFunc=None):
        if mapFunc:
            mapFunction = mapFunc
        else:
            mapFunction = self.mapFunc

        databags = []
        for d in list(self.db.temporary_query(mapFunction)):
            databags.append(Databag(d['value'].get('_id'), d['value'].get('data')))

        return databags
