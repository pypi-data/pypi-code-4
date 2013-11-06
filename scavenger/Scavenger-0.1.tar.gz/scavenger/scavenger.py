import os
import sys
import inspect
from difflib import get_close_matches
# import dependencies
try:
    import redis
except ImportError:
    print 'redis is required.'
    print '* verify your environment is properly configured or -> pip install redis'
try:
    from mongoengine import *
except ImportError:
    print 'mongoengine is required'
    print '* verify your environment is properly configured or -> pip install mongoengine'


class Scavenger():
    """
    Scavenger - simple search
    """
    def __init__(self, criteria, **kwargs):
        if kwargs.get('index_root'):
            self.index_root = kwargs.get('index_root')
        else:
            self.index_root = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
        if kwargs.get('redis_server'):
            self.r_server = kwargs.get('redis_server')
        else:
            self.r_server = redis.Redis(host='localhost', port=6379, db=0)
        self.criteria = criteria
        self.redis_data = self.get_redis_index()


    def get_redis_index(self):
        """
        Pre-fetch search criteria query handlers for index id sub parsing
        """
        data = []
        # Leaks are unmatched provided values of self.criteria.
        leaks = [False]
        for type_set in self.criteria:
            if self.r_server.smembers(self.index_root + ':' + type_set):
                for val in self.r_server.smembers(self.index_root + ':' + type_set):
                    data.append('%s' % val)
            # If value is not matched in redis index, 
            # leaks is returned to avoid searching on "null indexes"
            else:
                leaks.append(type_set)
        if len(leaks) > 1:
            return leaks
        return data


    def search(self, **kwargs):
        """
        Perform search against redis using user input query.
        """
        if self.redis_data[0]:
            if __name__ == '__main__':
                query = raw_input('Enter search criteria: ')
            else: 
                if kwargs.get('query'):
                    query = kwargs.get('query')
                else:
                    return 'No search query provided'
            match_ids = []
            for crit in self.criteria:
                match = get_close_matches(
                    query, 
                    self.r_server.smembers(self.index_root + ':' + crit)
                )
                if match:
                    for index in match:
                        match_ids = self.r_server.smembers('%s:%s:%s' % 
                            (self.index_root, crit, index))
            query_set = []
            for match_id in match_ids:
                exec('query_set.append(' + \
                    self.index_root.title() + '.objects.get(id="' + match_id + '"))')
            if query_set:
                return query_set
            else:
                print 'No matches found'
        else:
            self.redis_data.pop(0)
            print 'No indexes found for models:\n' + \
                str('\n'.join(['> %s' % model for model in self.redis_data]))


    @classmethod
    def index(mongoobj, **kwargs):
        """
        Index the provided mongodb object to redis model index
        """
        model = mongoobj.__class__.__name__.lower()
        mongoobj.save()
        if mongoobj.id:
            for field in mongoobj.indices:
                field_val = getattr(mongoobj, field)
                if field_val is not None and field_val != False:
                    print 'added "%s" to index' % field
                    redis_type_set = '%s:%s' % (model, str(field))
                    r_server.sadd(redis_type_set, getattr(mongoobj, field).lower())
                    redis_value_set = '%s:%s:%s' % (model, str(field), getattr(mongoobj, field).lower())
                    r_server.sadd(redis_value_set, mongoobj.id)
                else:
                    print '"%s" not added to index' % field
        else:
            print 'Item has no ID'


    # App About Information 
    version = '0.1'

    @classmethod
    def getver(self):
        """
        Get version information
        """
        print '---'
        print 'version: %s\n' % self.version,
        print '---'