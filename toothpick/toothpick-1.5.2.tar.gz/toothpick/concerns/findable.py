import toothpick

from toothpick import hooks

from toothpick import exceptions

class Findable(object):
    '''
    Mixin handling operations such as finding model instances based on queries,
    and verifying the existance of a document for a query.
    '''
    _find_options_key = "options"

    @hooks.hook_provider('find', only='after')
    def _found(self):
        '''
        Triggers the `after_find` hook, and marks all documents on this
        instance as "not new" (#save() will perform an update, as opposed to a
        create.)
        '''
        [self._new_documents.remove(key) for key in self._docs]

    @classmethod
    def find_one(cls, single_query=toothpick.DEFAULT, **queries):
        '''
        Returns exactly one instance of this model, according to the queries
        that are passed in.  If the passed queries produce 0 records, or more
        than one record, an exception is raised.
        '''
        coallated = cls._fetch_coallated_docs(single_query, **queries)
        if len(coallated) == 0:
            # TODO exceptions are totally attached to the http case - need
            # to be generalized
            raise exceptions.NotFound()
        if len(coallated) == 1:
            model = cls(coallated[0])
            model._found()
            return model
        else:
            raise exceptions.TooManyRecordsError("Found too many records!")


    @classmethod
    def find(cls, single_query=toothpick.DEFAULT, **queries):
        '''
        Returns a list of instances of this model, according to the queries
        that are pased in.  This list is empty if no records are found.
        '''
        models = []
        for coallated in cls._fetch_coallated_docs(single_query, **queries):
            model = cls(coallated)
            models.append(model)
            model._found()
        
        return models


    @classmethod
    def first(cls, single_query=toothpick.DEFAULT, **queries):
        '''
        Returns the first record found by the query arguments, or None if no
        records are found.
        '''
        models = cls.find(single_query, **queries)
        if len(models) == 0:
            return None
        return models[0]

    @classmethod
    def _fetch_coallated_docs(cls, single_query=toothpick.DEFAULT, **queries):
        '''
        Returns a list of dictionaries of the form:
            {
              resource_name: {document}
              ...
            }
        The returned list may be empty.

        '''
        # TODO: itertools.izip - iterator rather than temp var
        def tupleify(*args):
            return tuple(args)

        # extract the options key, if it's present 
        try:
            options = queries.pop(cls._find_options_key)
        except KeyError:
            options = {}

        # handle the single query case
        if single_query != toothpick.DEFAULT:
            if len(cls._resources) > 1:
                raise exceptions.ToothpickError(
                    "When more than one resource is declared for a model, " +
                    "the query resource cannot be inferred."
                )
            queries = { cls._resources.keys()[0]: single_query }


        # actually interrogate each resource, and make a dictionary with each
        # resource name in `queries` referring to a list of documents returned
        # by _fetch_docs
        resource_docs = {
            cls._resource(resource_name, 'read').resource_name : \
            cls._fetch_docs(resource_name, query, options)
            for resource_name, query in queries.items()
        }
        
        # coallate the above dictionary into a list of dictionaries appropriate
        # for e.g. the constructor
        return [
            dict(zip(resource_docs.keys(), docs))
            for docs in map(tupleify, *resource_docs.values())
        ]


    @classmethod
    def _fetch_docs(cls, resource_name, query, options=None):
        '''
        Returns a document in deserialized (hash) form.
        
        If model caching is used, then the cache will be checked
        for the document before going to the remote data endpoint.

        See toothpick/cache.py for more about caching.
        '''
        try:
            attributes = cls._resource(resource_name).read(
                query=query,
                options=options
            )
                                                  
            # things like #find are expecting lists of documents, even if there's
            # only one, but that seems a little artifact-y.  I'm putting that here
            # as a constraint rather than forcing Resource implementors to worry
            # about it.
            if not type(attributes) == type([]):
                attributes = [attributes]

            return attributes
        except exceptions.NotFound:
            return []

    @classmethod
    def exists(cls, **kwargs):
        '''
        Returns true if passing the same parameters to find will
        result in a successful resource instantiation (i.e. the resource
        is found on the server), false otherwise.
        '''
        return all([
            cls._document_exists(resource_name, query)
            for resource_name, query in kwargs.items()
        ])

    @classmethod
    def _document_exists(cls, resource_name, query):
        return cls._resource(resource_name, 'exists').exists(query=query)

