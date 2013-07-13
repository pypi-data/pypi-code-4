#class RethinkCollection(object):
    #"""
    #Base collection object providing access to groups of RethinkModels
    #"""
    #@classmethod
    #def all(cls):
        #"""
        #Returns a python list of model objects

        #:return: A list of `csl` instances containing all of the results
        #:rtype: List
        #"""
        #results = r.database(c.database.rethinkdb).table(cls._table)
        #resultsToCls = [ cls.load(id=result) for result in results ]

        #return resultsToCls

    #@classmethod
    #def find(cls, field, value):
        #"""
        #Runs a where search clause on the given field for the given value

        #:param field: Which filed should this search be completed on
        #:param value: The value to search for in the ORM
        #:return: Either a `cls` instance or a list of `cls` instances
            #if a result or multiple have been found.
            #`None` if no user is found
        #"""
        #pass
