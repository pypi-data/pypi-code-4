import toothpick

from toothpick import hooks

from toothpick import exceptions

class Persistable(object):
    '''
    Mixin to handle the create, update, and delete behavior provided by the
    Base classes of toothpick.
    '''


    def save(self, exception=True, validate=True):
        '''
        Persists member fields of this instance to the backend they
        are associated with through a resource.

        If `exception` is set to `False`, then `save()` returns `True` for
        success, and `False` otherwise.

        If `validate` is set to `False`, then the object is persisted without
        running validations.  Use with caution.

        '''
        if not validate or self.valid():
            self._persist_documents()
            self.evict()
        else:
            if exception:
                raise exceptions.RecordInvalidError(
                    "object is not valid. %s" % self.errors
                )
            else:
                return bool(self.errors)


    @hooks.hook_provider('save')
    def _persist_documents(self):
        for resource_name in self._docs.keys():
            if resource_name in self._new_documents:
                self._create_document(resource_name)
            else:
                self._update_document(resource_name)

    @hooks.hook_provider('create')
    def _create_document(self, resource_name):
        resource = self._resource(resource_name, 'create')

        try:
            query = self.generate_query(resource_name)
        except AttributeError:
            query = None

        result = resource.create(query, self._docs[resource_name])
        self._docs[resource_name].update(result)
        self._new_documents.remove(resource_name)

    @hooks.hook_provider('update')
    def _update_document(self, resource_name):
        resource = self._resource(resource_name, 'update')
        query = self.generate_query(resource_name)

        result = resource.update(query=query,
                                 attributes=self._docs[resource_name])


    @hooks.hook_provider('delete')
    def delete(self):
        '''
        Delete this object from all backends it is associated with.
        '''
        for resource_name in self._docs:
            if resource_name not in self._new_documents:
                resource = self._resource(resource_name, 'delete')
                query = self.generate_query(resource_name)
                result = resource.delete(query)
        self.evict()

    def generate_query(self, resource_name):
        '''
        This method returns an appropriate query for this instance for a given
        resource_name, a sort of reverse-lookup.
        '''
        return getattr(self, resource_name)


