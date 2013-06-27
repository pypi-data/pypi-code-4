from pymongo import MongoClient 
from pymongo.collection import Collection 
from pymongo.errors import CollectionInvalid
#from pymongo.errors import ConnectionFailure

# needed for write
from socket import getfqdn
from time import time

# needed for tail
from prettyprint import pp
from time import sleep

class Logmongo(Collection):
    def __init__(self, name, db='logs',
            size=524288000, capped=True, host='localhost', port=27017):

        database = MongoClient(host=host,port=port )[db]

        try: # attempt to create capped collection
            database.create_collection(
                name,
                capped=capped,
                size=size
            )
        except CollectionInvalid: # collection exists
            pass
        
        # run the super parent's init!
        super(Logmongo, self).__init__(database, name)

    def write( self, record=None, **kwargs ):
        """Log all kwargs with timestamp to collection"""
        record = self._unite(record,kwargs)
        record['when'] = int(time() * 100)
        record['source'] = getfqdn()
        self.save( record, w=0 ) # w=0: do not wait for success/fail or error

    def query( self, record=None, **kwargs ):
        """just like find, but accepts kwargs for query"""
        record = self._unite(record,kwargs)
        return self.find( record )

    def _unite(self,record,kwargs):
        if record:
            return dict( record.items() + kwargs.items() )
        else:
            return kwargs

    def tail( self, query=None, n=10 ):    
        """print all entries that match query until killed"""

        nskip = self.count() - n

        if nskip < 0: nskip = 0
     
        if query == None: query = {}
 
        cursor = self.find( query, tailable=True, skip=nskip )

        while cursor.alive:
            try:
                entry = cursor.next()
                pp( entry ) 
            except StopIteration:
                sleep(1)

    def update( self ):
        """logs should not be updated"""
        pass

    def remove( self ):
        """logs should not be removed, maybe set archive bit?"""
        pass

