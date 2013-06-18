import inflection

class Errors(object):
    '''
    The `Errors` object is a container of validation errors stored on an
    instance of a :class:`Base` subclass.  An object's validation
    state (and the response to :meth:`Base.valid()`) is governed by the number
    of errors collected: 0 means valid, and more means invalid.  

    The errors are represented as tuples of (attribute_name, error_message).

    This class provides several methods for accessing the errors it stores:

        >>> model.errors
        [('name', "can't be blank"), ('age', "must be greater than 18")]
        
        >>> model.errors['name']
        ["can't be blank"]

        >>> model.errors.messages()
        ["Name can't be blank", "Age must be greater than 18"]
        
        >>> model.errors.messages('name')
        ["Name can't be blank"]

    '''

    def __init__(self):
        self.clear()

    def __getitem__(self, attribute_name):
        '''
        Returns a list of error messages for a given attribute.
        '''
        return [i[1] for i in self._store if i[0] == attribute_name]

    def __len__(self):
        return len(self._store)

    def __iter__(self):
        return iter(self._store)

    def __repr__(self):
        return repr(self._store)

    def add(self, field_name, error_msg):
        '''
        Adds an error to this instance.
        '''
        self._store.append((field_name, error_msg))

    def clear(self):
        '''
        Removes all errors from this instance
        '''
        self._store = []

    def messages(self, attribute_name=None):
        '''
        Returns a humanized string representing the errors contained in this
        instance.  if `attribute_name` is passed, then only errors for that
        attribute are considered.
        '''
        if attribute_name:
            return [self._messagify(i[0], i[1], inflection.humanize)
                    for i in self._store if i[0] == attribute_name]
        else:
            return [self._messagify(i[0], i[1], inflection.humanize)
                    for i in self._store]

    def api_messages(self, attribute_name=None):
        '''
        Like `#messages()`, but keeps the field names in their non-humanized form.
        '''
        if attribute_name:
            return [self._messagify(i[0], i[1]) for i in self._store
                    if i[0] == attribute_name]
        else:
            return [self._messagify(i[0], i[1]) for i in self._store]

    @classmethod
    def _messagify(cls, field_name, error_msg, transformer=None):
        if not transformer:
            transformer = lambda x: "'%s'" % x

        if not field_name:
            return error_msg

        return "%s %s" % (
            transformer(field_name),
            error_msg
        )






