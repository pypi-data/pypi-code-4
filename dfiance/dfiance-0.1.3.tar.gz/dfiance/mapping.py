from collections import OrderedDict

from base import Dictifier, ErrorAggregator, Invalid, Field
from basic import String

class SchemaMapping(Dictifier):
    '''Dictifier for structured dicts.

    The field_types variable describes the type to dictify as an ordered
    dictionary mapping dictionary keys to dictifiers for those keys.

    >>> from basic import Int
    >>> from datetypes import Date
    >>> from datetime import date
    >>> bday = date(1985, 9, 16)
    >>> schema = SchemaMapping(dict(age=Int(), birthday=Date()))
    >>> cstruct = schema.dictify(dict(age=27, birthday=bday))
    >>> cstruct == dict(age=27, birthday=u'1985-09-16')
    True
    >>> schema.undictify(cstruct) == dict(age=27, birthday=bday)
    True
    >>> schema.validate(dict(age=27, birthday=bday))
    >>> schema.validate(dict(age=27.1, birthday="not a date"))
    Traceback (most recent call last):
    ...
    Invalid: age: [type_error], birthday: [type_error]

    The 'extra_field_policy' flag should be 'save', 'ignore', or 'error'. This
    controls what happens on undictifiance when unexpected fields are present.

    On 'save', extra fields are stored in the returned dictionary under the key
    _extras:

    >>> schema = SchemaMapping(dict(age=Int()), 'save')
    >>> v = schema.undictify({'age':27, 'color':'blue'})
    >>> v == {'age': 27, '_extras': {'color': 'blue'}}
    True

    On 'error', extra fields cause an Invalid exception:

    >>> schema = SchemaMapping(dict(age=Int()), 'error')
    >>> v = schema.undictify({'age':27, 'color':'blue'})
    Traceback (most recent call last):
    ...
    Invalid: ('unexpected_fields', {'keys': set(['color'])})

    On 'ignore', extra fields are discarded:

    >>> schema = SchemaMapping(dict(age=Int()), 'ignore')
    >>> v = schema.undictify({'age':27, 'color':'blue'})
    >>> v == {'age': 27}
    True

    If the entries in field_types are Fields, they are used directly; if not,
    they're wrapped in Fields with not_none=False (so that None is legal):

    >>> schema = SchemaMapping(dict(age=Int()))
    >>> schema.validate({'age':None})
    >>> schema = SchemaMapping(dict(age=Field(Int(), not_none=True)))
    >>> schema.validate({'age':None})
    Traceback (most recent call last):
    ...
    Invalid: age: [empty]
    '''
    def __init__(self, field_types, extra_field_policy="ignore"):
        super(SchemaMapping, self).__init__()
        self.field_types = OrderedDict()
        for key, field_or_dfier in field_types.iteritems():
            self.field_types[key] = Field.asfield(field_or_dfier)
        self.extra_field_policy=extra_field_policy

    def _handle_fields(self, value, error_agg, kwargs):
        '''Undictify our fields. Override this to customize subfields.'''
        data = {}
        for key, type in self.field_types.iteritems():
            with error_agg.checking_sub(key):
                val = value.get(key, None)
                data[key] = type.undictify(val, **kwargs)
        return data

    def _handle_extras(self, value, error_agg, kwargs):
        '''Process any keys in value that aren't expected fields.

        If self.extra_field_policy is 'save', these values will be stored in
        _extras; if it's 'error', they'll be added as errors. Otherwise they'll
        be ignored.
        '''
        if self.extra_field_policy not in ['save', 'error']:
            return None
        extra_keys = set(value.keys()) - set(self.field_types.keys())
        if not extra_keys: return
        if self.extra_field_policy == 'save':
            extras = dict()
            for key in extra_keys:
                extras[key] = value[key]
            return extras
        else:
            error_agg.own_error(Invalid('unexpected_fields', keys=extra_keys))
            return None

    def undictify(self, value, **kwargs):
        if value is None:
            value = {}
        if not isinstance(value, dict):
            raise Invalid('not_dict')
        # If fail_early is True, then gather all errors from this and its
        # children. Otherwise, just raise the first error we encounter.
        error_agg = ErrorAggregator(autoraise = kwargs.get('fail_early', False))
        data = self._handle_fields(value, error_agg, kwargs)
        extras = self._handle_extras(value, error_agg, kwargs)
        if extras:
            data['_extras'] = extras
        error_agg.raise_if_any()
        return data

    def dictify(self, value, **kwargs):
        result = {}
        for key, typ in self.field_types.items():
            result[key] = typ.dictify(value[key])
        if self.extra_field_policy == 'save':
            for key, val in self._extras.items():
                if key not in result:
                    result[key] = val
        return result

    def validate(self, value, **kwargs):
        error_agg = ErrorAggregator(autoraise = kwargs.get('fail_early', False))
        with error_agg.checking():
            super(SchemaMapping, self).validate(value, **kwargs)
        for field, type in self.field_types.iteritems():
            with error_agg.checking_sub(field):
                type.validate(value[field])
        error_agg.raise_if_any()

    def sub_dfier_keys(self, value=None):
        return self.field_types.keys()

    def sub_dfier(self, key, value=None):
        return self.field_types[key]

    def sub_value_keys(self, value):
        return self.sub_dfier_keys()

    def sub_value(self, value, key):
        return value[key]

class UniMapping(Dictifier):
    '''Dictifier for dicts with homogenous keys and homogenous values.

    The key_type and val_type variables determine the types of the keys and the
    values in the mapping, which should all be the same types.

    >>> from basic import Int
    >>> from datetypes import Date
    >>> from datetime import date
    >>> bday = date(1985, 9, 16)
    >>> NumToDate = UniMapping(key_type=Int(), val_type=Date())
    >>> cstruct = NumToDate.dictify({27:bday})
    >>> cstruct == {27:u'1985-09-16'}
    True
    >>> NumToDate.undictify(cstruct) == {27:bday}
    True
    >>> NumToDate.validate({27:bday})
    >>> NumToDate.validate({27.1:"not a date"})
    Traceback (most recent call last):
    ...
    Invalid: key_0: [type_error], value_0: [type_error]

    If the entries in field_types are Fields, they are used directly; if not,
    they're wrapped in Fields with not_none=False (so that None is legal):

    >>> StrToNum = UniMapping(val_type=Int())
    >>> StrToNum.validate({'age':None})
    >>> StrToNum = UniMapping(val_type=Field(Int(), not_none=True))
    >>> StrToNum.validate({'age':None})
    Traceback (most recent call last):
    ...
    Invalid: value_0: [empty]
    '''
    def __init__(self, val_type, key_type=None):
        super(UniMapping, self).__init__()
        if key_type is None:
            key_type = Field(String(), not_none=True)
        self.key_type = Field.asfield(key_type)
        self.val_type = Field.asfield(val_type)

    def _handle_fields(self, value, error_agg, kwargs):
        '''Undictify our fields. Override this to customize subfields.'''
        data = {}
        for key, type in self.field_types.iteritems():
            with error_agg.checking_sub(key):
                val = value.get(key, None)
                data[key] = type.undictify(val, **kwargs)
        return data

    def undictify(self, value, **kwargs):
        if value is None:
            value = {}
        if not isinstance(value, dict):
            raise Invalid('not_dict')
        # If fail_early is True, then gather all errors from this and its
        # children. Otherwise, just raise the first error we encounter.
        error_agg = ErrorAggregator(autoraise = kwargs.get('fail_early', False))
        data = {}
        for i, (key, val) in enumerate(value.items()):
            with error_agg.checking_sub('key_{}'.format(i)):
                key = self.key_type.undictify(key, **kwargs)
            with error_agg.checking_sub('value_{}'.format(i)):
                val = self.val_type.undictify(val, **kwargs)
            data[key] = val
        error_agg.raise_if_any()
        return data

    def dictify(self, value, **kwargs):
        kdfy = lambda x: self.key_type.dictify(x, **kwargs)
        vdfy = lambda x: self.val_type.dictify(x, **kwargs)
        return {kdfy(key):vdfy(val) for (key, val) in value.items()}

    def validate(self, value, **kwargs):
        error_agg = ErrorAggregator(autoraise = kwargs.get('fail_early', False))
        with error_agg.checking():
            super(UniMapping, self).validate(value, **kwargs)
        for i, (key, val) in enumerate(value.items()):
            with error_agg.checking_sub('key_{}'.format(i)):
                self.key_type.validate(key, **kwargs)
            with error_agg.checking_sub('value_{}'.format(i)):
                self.val_type.validate(val, **kwargs)
        error_agg.raise_if_any()

    # No notion of iterated access to elements, so this can't be used in a graph

    def sub_dfier_keys(self, value=None):
        return ()

    def sub_dfier(self, key, value=None):
        raise KeyError(key)

    def sub_value_keys(self, value):
        return ()

    def sub_value(self, value, key):
        raise KeyError(key)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
