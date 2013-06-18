from collections import MutableSequence

import inflection
from toothpick import exceptions, logger

UNRESOLVED = object()

class Association(object):
    '''
    Create an association with another model.  The association will
    be populated with an instance of the class indicated by `other_model`,
    using the resource specified by `resource_name`, with the contents of
    `data_field` on this instance used as a query parameter.

    Associations support a few options:
        * soft: if the associated object does not exist, either None is
          returned as the associated model, or that associated model is omitted
          from the list of associated models, in the case of Single- or
          MultipleAssociations, respectively.

        * data_resource: when performing an assignment on an association, a
          foreign key from one object is stored on another.  If the field that
          should hold the foreign key on the owning side isn't attached to a
          resource yet, then it's attached to the resource named by this
          string, if it's provided.
    '''

    def __init__(self, other_model, resource_name, 
                 data_field, foreign_key=None, **options):
        self.other_model_or_str = other_model
        self.resource_name = resource_name
        self.foreign_key = foreign_key
        self.data_field = data_field

        self.resolved = UNRESOLVED

        self.options = dict(
            soft=False,
            data_resource=None,
        )
        self.options.update(options)

    def copy(self):
        return type(self)(
            other_model=self.other_model_or_str,
            resource_name=self.resource_name,
            data_field=self.data_field,
            **self.options
            # foreign_key intentionally omitted
        )

    def __get__(self, instance, cls=None):
        if self.resolved == UNRESOLVED:
            self.resolved = self.resolve(instance)

        return self.resolved


    def get_foreign_key(self, instance):
        # don't use getattr here, because if we collide with an association
        # name, we infinitely loop.
        return instance._get_attribute(self.data_field, None)


    def set_foreign_key(self, instance, value):
        if self.options['data_resource']:
            instance.add_field(self.options['data_resource'], self.data_field)
        instance._set_attribute(self.data_field, value)
        self.foreign_key = value

    def _verify_incoming(self, model):
        if not isinstance(model, self.other_model):
            raise ValueError(
                "Association is wrong type for incoming model: %s is not %s" % (
                    self.other_model.__name__,
                    model.__class__.__name__
                )
            )

    @property
    def other_model(self):
        '''
        Convenience method to handle the resolution of the other side of the
        association.  This can't be done in the association constructor, 
        because that would disrupt the lazy nature of associations and cause
        some nasty loops.
        '''
        import toothpick
        if isinstance(self.other_model_or_str, str):
            return toothpick.find_model(self.other_model_or_str)
        else:
            return self.other_model_or_str


class SingleAssociation(Association):
    """ 1:* relations """

    def resolve(self, instance):
        if not self.foreign_key:
            data = self.get_foreign_key(instance)
            if data == None:
                return self._empty_resolution

            self.foreign_key = data


        foreign_key = self.foreign_key

        query = {self.resource_name: foreign_key}
        if self.options['soft'] and not self._check_model_exists(query):
            return self._empty_resolution

        return self._instantiate_model(query, instance)

    def _check_model_exists(self, data):
        exists = self.other_model.exists(**data)
        # compensate for a bug/issue in RedisCache
        if exists == 'False':
            return False
        return exists

    def _instantiate_model(self, data, instance):
        return self.other_model.find_one(**data)

    @property
    def _empty_resolution(self):
        return None

    def update(self, instance, incoming):
        '''
        Used to allow an association to be set.

        Currently will not work when incoming is not saved.
        '''
        if incoming == self._empty_resolution:
            return self.clear(instance)
        self._verify_incoming(incoming)


        # TODO: duplicated
        # set the foreign key on the association, for completeness
        self.foreign_key = self._process_incoming(incoming)

        # set the cached associated object
        self.resolved = incoming

        # set the foreign key on the object, so the new assoc. sticks
        self.set_foreign_key(instance, self.foreign_key)


    def _process_incoming(self, incoming):
        return incoming.generate_query(self.resource_name)


    def clear(self, instance):
        '''
        Clears the association and the foreign key on the associated model
        '''
        self.resolved = self._empty_resolution
        self.set_foreign_key(instance, None)


    def evict(self, instance):
        if self.foreign_key:
            foreign_key = self.foreign_key
        else:
            foreign_key = self.get_foreign_key(instance)
            
        return self.other_model.evict_document(
            **{ self.resource_name: foreign_key }
        )


class SingleEmbeddedAssociation(SingleAssociation):
    # Note - this class uses the `foreign_key` attribute to store (a reference
    # to) the actual document, because that's what's stored on the parent model
    # under that parameter.

    def _check_model_exists(self, data):
        return bool(data.values())

    def _instantiate_model(self, data, instance):
        model = self.other_model(docs=data)
        model._embedded_owner = instance
        return model

    def _process_incoming(self, incoming):
        return incoming._docs[self.resource_name]

    def evict(self, instance):
        pass # embedded models aren't cacheable





class MultipleAssociation(Association):
    """ n:* associations """
    single_cls = SingleAssociation

    def resolve(self, instance):
        query_set = self.get_foreign_key(instance)
        associations = AssociationList(instance, self)

        if query_set == None:
            return associations

        for query in query_set:
            associations.append_association(
                self.single_cls(
                    other_model=self.other_model_or_str,
                    resource_name=self.resource_name,
                    data_field=None,
                    foreign_key=query,
                    **self.options
                )
            )

        return associations


    def update(self, instance, incoming):
        if incoming == None:
            incoming = []

        # new AssociationList to replace what's in resolved
        associations = AssociationList(instance, self)

        UNSET = object()

        try:
            old_foreign_keys = self.get_foreign_key(instance)
        except:
            old_foreign_keys = UNSET

        # we're going to be using append, so we need to be appending to
        # a clean list
        self.set_foreign_key(instance, [])

        try:
            for model in incoming:
                associations.append(model)
            self.resolved = associations
        except Exception, e:
            if old_foreign_keys != UNSET:
                self.set_foreign_key(instance, old_foreign_keys)
            raise e

    def clear(self, instance):
        self.update(instance, [])

    def evict(self, instance):
        for association in self.__get__(instance)._descriptor_objects():
            association.evict(instance)

    def _process_incoming(self, model):
        return model.generate_query(self.resource_name)

class MultipleEmbeddedAssociation(MultipleAssociation):
    single_cls = SingleEmbeddedAssociation

    def _process_incoming(self, model):
        return model._docs[self.resource_name]




class AggregateAssociation(MultipleAssociation):

    def resolve(self, instance):
        query = { self.resource_name: self.get_foreign_key(instance) }
        associations = AssociationList(instance, self)
        
        models = self._instantiate_model(query, instance)
        for model in models:
            association = SingleAssociation(
                other_model=self.other_model_or_str,
                resource_name=None,
                data_field=None,
                foreign_key=None,
                **self.options)
            association.resolved = model
            associations.append_association(association)

        return associations


    def update(self, instance, incoming):
        raise NotImplementedError("Can't set an aggregate association")

    def clear(self, instance):
        raise NotImplementedError("Can't clear an aggregate association")

    def set_foreign_key(self, instance, value):
        raise NotImplementedError("Can't set the data field on an aggregate \
                                  association")

    def _instantiate_model(self, data, instance):
        return self.other_model.find(**data)

    @property
    def _empty_resolution(self):
        return []


from collections import MutableSequence

class DescriptorList(MutableSequence):
    def __init__(self, instance, items=None):
        super(DescriptorList, self).__init__()
        self.instance = instance
        if not items:
            items = []
        self.l = items

    def __len__(self):
        return len(self.l)

    def __getitem__(self, index):
        r = self.l[index]
        if type(index) == slice:
            return [self.as_descriptor(x) for x in r]
        return self.as_descriptor(r)

    def __setitem__(self, index, value):
        self.l[index] = value

    def __delitem__(self, index):
        del self.l[index]

    def insert(self, index, value):
        self.l.insert(index, value)
    
    def as_descriptor(self, obj):
        if hasattr(obj, '__get__'):
            return obj.__get__(self.instance, type(self.instance))
        return obj

    def _descriptor_objects(self):
        for item in self.l:
            yield item

    def __repr__(self):
        return repr(self[:])


class AssociationList(DescriptorList):
    '''
    Subclass to keep association-specific functionality out of
    DescriptorList, which could conceivable be used for other
    purposes.
    '''
    # TODO: pull foreign keys / resource data into this class, and
    # collapse it into MultipleAssociation.

    def __init__(self, instance, association, items=None):
        super(AssociationList, self).__init__(instance, items)
        self.association = association

    def insert(self, index, model):
        import toothpick
        self.association._verify_incoming(model)
                
        # in the embedded case, foreign_key = data
        foreign_key = self.association._process_incoming(model)
        
        foreign_keys = self.association.get_foreign_key(self.instance)
        if foreign_keys == None:
            foreign_keys = []

        foreign_keys.insert(index, foreign_key)

        new_association = self.association.single_cls(
            other_model=self.association.other_model_or_str,
            resource_name=self.association.resource_name,
            data_field=None,
            foreign_key=foreign_key,
            **self.association.options
        )
        new_association.resolved = model

        if isinstance(model, toothpick.EmbeddedBase):
            model._embedded_owner = self.instance

        self.association.set_foreign_key(self.instance, foreign_keys)

        return self.insert_association(index, new_association)

    def __delitem__(self, index):
        foreign_keys = self.association.get_foreign_key(self.instance)
        if foreign_keys == None:
            foreign_keys = []

        del foreign_keys[index]
        self.association.set_foreign_key(self.instance, foreign_keys)

        return super(AssociationList, self).__delitem__(index)

    def index(self, model):
        self.association._verify_incoming(model)

        foreign_key = self.association._process_incoming(model)

        for i, v in enumerate(self):
            if self.association._process_incoming(v) == foreign_key:
                return i
        raise ValueError
    
    def valid(self):
        return all([item.valid() for item in self])


    def insert_association(self, index, association):
        return super(AssociationList, self).insert(index, association)

    def append_association(self, association):
        return self.insert_association(len(self), association)








# These helper methods, thus far, have no additional logic of their
# own to enforce the behavior described. They are merely semantic
# labels describing the associations within.
def has_many(other_model, resource_name = "id", data_field = None, **options):
    if options.pop('aggregate', None):
        association_class = AggregateAssociation
    else:
        association_class = MultipleAssociation
        if data_field == None:
            data_field = _guess_data_field(other_model, True)

    return association_class(other_model, resource_name, data_field, **options)

def belongs_to(other_model, resource_name = "id", data_field = None, **options):
    if data_field == None:
        data_field = _guess_data_field(other_model, False)
    return SingleAssociation(other_model, resource_name, data_field, **options)

def belongs_to_many(other_model, resource_name = "id", data_field = None, **options):
    return has_many(other_model, resource_name, data_field, **options)

def has_a(other_model, resource_name = "id", data_field = None, **options):
    return belongs_to(other_model, resource_name, data_field, **options)


def _guess_data_field(model_class_or_name, plural = False):
    '''If the helper methods are called with a data_field of None, then
    this method is used to guess at what the field is named.  It looks
    at the class name of other_model, and adds either '_id' or '_ids'.'''

    if not isinstance(model_class_or_name, str):
        model_class_or_name = model_class_or_name.__name__

    suffix = ""
    if plural:
        suffix = "s"

    return "%s_id%s" % (inflection.underscore(model_class_or_name), suffix)

def embeds_a(other_model, resource_name, data_field, **options):
    return SingleEmbeddedAssociation(
        other_model, resource_name, data_field, **options
    )

def embeds_many(other_model, resource_name, data_field, **options):
    return MultipleEmbeddedAssociation(
        other_model, resource_name, data_field, **options
    )

