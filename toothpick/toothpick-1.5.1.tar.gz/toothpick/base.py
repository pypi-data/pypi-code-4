import toothpick
import toothpick.validations

from toothpick import hooks

from toothpick.associations import Association

from toothpick.concerns.persistable import Persistable
from toothpick.concerns.findable import Findable
from toothpick.concerns.comparable import Comparable
from toothpick.concerns.cacheable import Cacheable
from toothpick.concerns.validatable import Validatable
from toothpick.concerns.has_attributes import HasAttributes
from toothpick.concerns.has_resources import HasResources
from toothpick.concerns.serializable import Serializable
from toothpick.concerns.displayable import Displayable

from toothpick import register_model, find_model

import inspect

class BaseMetaclass(type):
    """Metaclass for base class"""

    def __new__(cls, name, bases, attrs):
        new_attrs = {}
        associations = {}
        validators = []
        hooks = {}

        for attr_name, attr in attrs.items():
            if isinstance(attr, Association):
                # need to make a copy of the association, to preserve
                # instance-level attribs of the association
                associations[attr_name] = attr
            else:
                new_attrs[attr_name] = attr

            if toothpick.validations._is_validator(attr):
                validators.append(attr)

            for hook_name in toothpick.hooks._which_hook(attr):
                hooks_for_name = hooks.get(hook_name, [])
                hooks_for_name.append(attr)
                hooks[hook_name] = hooks_for_name

        # handle validators and hooks declared in other classes
        for base in bases:
            validators.extend(cls.find_validators(base))
            for hook_name, hook_methods in cls.find_hooks(base).items():
                hooks_for_name = hooks.get(hook_name, [])
                hooks_for_name.extend(hook_methods)
                hooks[hook_name] = hooks_for_name


        special_attrs = dict(
            _cls_associations=associations,
            _hooks=hooks,
        )

        if any([issubclass(base, HasResources) for base in bases]):
            special_attrs['_resources'] = dict()

        if any([issubclass(base, Validatable) for base in bases]):
            special_attrs['_validators'] = validators

        new_attrs.update(special_attrs)

        return register_model(name, type.__new__(cls, name, bases, new_attrs))
        # ^ substituting for `return type.__new__(cls, name, bases, new_attrs)`

    @classmethod
    def find_validators(cls, base):
        validators = []
        for method_name, method in inspect.getmembers(base, inspect.ismethod):
            if toothpick.validations._is_validator(method):
                validators.append(method)
        return validators

    @classmethod
    def find_hooks(cls, base):
        hooks = {}
        for method_name, method in inspect.getmembers(base, inspect.ismethod):
            for hook_name in toothpick.hooks._which_hook(method):
                hooks_for_name = hooks.get(hook_name, [])
                hooks_for_name.append(method)
                hooks[hook_name] = hooks_for_name
        return hooks


class BaseInitializer(object):
    @hooks.hook_provider('init', only='after')
    def __init__(self, docs = None):
        # TODO: it would be nice if this init was actually broken down and each
        # part lived in its appropriate mixin init

        if not docs:
            docs = {}

        # we must preserve the passed in document object, so we're going to
        # update that from the schema
        schema = self._infer_docs(self.schema)
        docs = self._infer_docs(docs)

        for resource, doc in schema.items():
            if docs.has_key(resource):
                # preserve the original document reference
                for attribute, value in doc.items():
                    if attribute not in docs[resource]:
                        docs[resource][attribute] = value
            else:
                docs[resource] = schema[resource]

        # a hash mapping the resource name to the doc it found
        self._docs = docs

        # a hash mapping actual association instances to their method
        # names, so that calling on an associated model doesn't force
        # it to be constructed anew each time.
        self._associations = {
            name : association.copy()
            for name, association in self._cls_associations.items()
        }

        # when a document is persisted, it is 'created' if it's a new
        # document, and 'updated' if it's not.
        self._new_documents = set(self._resources.keys())

        self.errors = toothpick.Errors()


        super(BaseInitializer, self).__init__()
        
        # hack to get around the fact that we've overridden __setattr__,
        # but want normal behavior in the constructor.
        self._initialized = True

        

_base_transients = [
    '_docs',
    '_new_documents',
    '_associations',
    'errors',
]

_embedded_base_transients = [
    '_embedded_owner',
]

class Base(BaseInitializer, Findable, Persistable, Comparable, Cacheable,
           Validatable, HasAttributes, HasResources, Serializable,
           Displayable):
    """Base class for toothpick models"""
    __metaclass__ = BaseMetaclass


class EmbeddedBase(BaseInitializer, Comparable, Validatable, HasAttributes,
                   HasResources, Serializable, Displayable):
    """Base class for embedded toothpick models"""
    __metaclass__ = BaseMetaclass

    
