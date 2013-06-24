import toothpick

from toothpick import hooks

class HasAttributes(object):
    '''
    Mixin for attribute-style access, and other attribute-related pieces
    '''

    @property
    def schema(self):
        '''
        Override to give a model a default schema.
        '''
        return {}

    def _infer_docs(self, docs):
        '''
        Attempts to "do the right thing" with a hash that's passed in to the
        constructor.  If the keys of the dictionary match the resource names,
        then we'll assume it's a properly-formed dictionary of documents.

        If it's not that, but it's still a dictionary, then we'll use it as the
        document only if the model only has one resource declared.
        
        Otherwise, who knows what it is, and we're going to take exception.
        '''
        try:
            if all([key in self._resources for key in docs.keys()]) and \
               all([hasattr(value, 'keys') for value in docs.values()]):
                # we've got a well-formed document dict
                return docs
            else:
                if len(self._resources) > 1:
                    raise ValueError("Must specify resource for document")
                else:
                    return { self._resources.keys()[0]: docs }
        except AttributeError:
            raise TypeError("Passed non-dictionary to constructor!")


    def __getattr__(self, method_name):
        # look for #method_name as an association
        if method_name in self._associations:
            return self._get_association(method_name)
        return self._get_attribute(method_name)
    
    def _get_association(self, association_name):
        # __get__ is not auto-called here because method_name is not
        # in the instance dictionary. (python descriptors)
        return self._associations[association_name].__get__(self, type(self))

    def _get_attribute(self, attribute_name, default=toothpick.DEFAULT):
        # look in the documents backing this object
        for doc in self._docs.values():
            if doc.has_key(attribute_name):
                # just return the value
                return doc[attribute_name]
        
        try:
            # we're calling __getattribute__ here because object doesn't have a
            # __getattr__ method.
            return super(HasAttributes, self).__getattribute__(attribute_name)
        except AttributeError, e:
            if default == toothpick.DEFAULT:
                raise e

        return default


    def __setattr__(self, method_name, value):
        if '_initialized' in self.__dict__ and not self._transient(method_name):
            if method_name in self._associations:
                return self._set_association(method_name, value)

            self._set_attribute(method_name, value)

        else:
            return super(HasAttributes, self).__setattr__(method_name, value)

    def _set_association(self, association_name, obj):
        return self._associations[association_name].update(self, obj)

    @hooks.hook_provider('modification')
    def _set_attribute(self, attribute_name, value):
        for resource_name, doc in self._docs.items():
            if doc.has_key(attribute_name):
                doc[attribute_name] = value
                return

        # fall through
        raise AttributeError(
            "Can't set an attribute that's not tied to a resource"
        )

    def add_fields(self, resource_name, *field_names, **fields):
        '''
        Add a field or fields to this object.  The `resource_name` parameter
        is used to specify which resource this field should be sent to
        during a `save` operation.
        
        Any field passed as a positional argument (captured by `field_names`)
        will be attached to the document specified by `resource_name` with
        a value of `None`.

        Any field passed as a keyword argument (captured by `fields`)
        will be attached to the document specified by `resource_name` with
        the value indicated by the dictionary.
        '''
        if resource_name not in self._resources:
            raise AttributeError("'%s' has no resource '%s'" % (
                self._model_name(), resource_name
            ))

        # initialize fields passed both with values and without
        field_names = list(field_names)
        field_names.extend(fields.keys())

        doc = self._docs.get(resource_name, {})
        for field in field_names:
            if field not in doc:
                doc[field] = None

        self._docs[resource_name] = doc

        # set values if we have 'em
        for field_name, value in fields.items():
            setattr(self, field_name, value)


    add_field = add_fields

    def _transient(self, attribute_name):
        '''
        Returns true if `attribute_name` references a transient attribute.
        Transient attributes are not attached to any document and are not
        persisted to any resource, but may be get and set on an instance.
        '''
        return any([
            attribute_name in toothpick.base._base_transients,
            attribute_name in toothpick.base._embedded_base_transients,
            attribute_name in getattr(self, 'transients', []),
        ])

    def _cached_attributes(self):
        return [x for doc in self._docs.values() for x in doc.keys()]

    # make this class act like the easy dictionary it's always wanted to be
    # does not work in testing, with prepopulated fields
    def items(self):
        return [(k,self._get_attribute(k)) for k in self._cached_attributes()]

