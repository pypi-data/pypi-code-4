from toothpick import hooks
from toothpick import cache

class Cacheable(object):
    _uses_toothpick_cache = False # unless @cached_model

    @hooks.hook_provider('eviction')
    def evict(self):
        '''
        In order to evict the documents represented by a specific instance from
        the cache, pass that object as the instance parameter.  All documents
        for which a query can be generated using `Resource`s attached to this
        class will be removed from the cache.  In this case, the keyword
        arguments passed explicitly are ignored.

        Additionally, all of the associations bound to this instance will be
        removed from the cache, but just through the associated resource.
        '''
        if self._uses_toothpick_cache:
            for resource_name in self._resources:
                resource = self._resource(resource_name)
                try:
                    # construct a query for every resource on this instance, and
                    # evict it from cache
                    self.evict_document(
                        resource_name, self.generate_query(resource_name)
                    )
                except AttributeError:
                    pass # couldn't construct query for that resource


            # evict all associations on this instance
            for association in self._associations.values():
                association.evict(self)


    @classmethod
    def evict_document(cls, resource_name, query):
        '''
        Remove a document from the cache, if it's there.  Keyword arguments
        passed to this method will be used to generate cache keys corresponding
        to keys generated and stored from keyword arguments passed to a single
        call of `Base.find()` or `Base.exists()`.  Those keys will be removed
        from the cache, if present.
        '''
        if cls._uses_toothpick_cache:
            # here we're actually forming the cache keys to delete

            # clear the 'fetch_doc' cache entry
            find_cache_key = cls._fetch_docs.cache_key(
                f=cls._fetch_docs,
                resource_name=resource_name,
                query=query,
            )
            cache.delete(find_cache_key)

            # also clear the 'exists' entry
            exists_cache_key = cls._document_exists.cache_key(
                f=cls._document_exists,
                resource_name=resource_name,
                query=query,
            )

                
            cache.delete(exists_cache_key)


