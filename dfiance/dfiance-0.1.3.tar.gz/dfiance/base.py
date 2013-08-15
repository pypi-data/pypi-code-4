from abc import ABCMeta, abstractmethod

from error_aggregator import ErrorAggregator as _ErrAgg, NestedException


class SingleInvalid(Exception):
    '''Base class for all undictification errors.

    In general, self.message will be a string indicating the specific error,
    e.g. 'required' when a value is missing that shouldn't be, 'not_int' for
    a value that must be an integer but cannot be parsed as one, and so forth.
    The specific errors raised by various Dictifiers are class-specific.
    '''
    def __init__(self, message=None, **kwargs):
        if kwargs:
            super(SingleInvalid, self).__init__(message, kwargs)
        else:
            super(SingleInvalid, self).__init__(message)
        self.message = message
        self.kwargs = kwargs

    def flatten(self):
        return dict(message=self.message, kwargs=self.kwargs)


class Invalid(NestedException):
    '''Base class for undictification errors of nested objects.

    This allows dictifiable types with sub-fields to record the errors from
    their subfields as well.
    '''
    def __init__(self, message=None, **kwargs):
        super(Invalid, self).__init__()
        if message or kwargs:
            self.own_errors.append(SingleInvalid(message, **kwargs))


class ErrorAggregator(_ErrAgg):
    '''Specialized ErrorAggregator to only aggregate Invalids'''
    error_type = Invalid
    catch_type = Invalid


class Validator(object):
    __metaclass__ = ABCMeta
    '''Abstract base class for Validators.'''
    def validate(self, value, **kwargs):
        return


class Dictifier(Validator):
    '''Abstract base class for Dictifiers.'''
    @abstractmethod
    def dictify(self, value, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def undictify(self, value, **kwargs):
        raise NotImplementedError()

    #
    # These four functions expose the graph structure of nested Dictifiers.
    # Each dfier can have sub dfiers, and each value that can be dictified can
    # have sub-values. The structure of the two graphs may be different. For
    # example, a "list of integers" dfier has "integer" as a single sub-dfier,
    # but a actual list of integer values has each integer as a sub-value.
    #
    # You can pass a value in when walking the structure of the dfier. This is
    # ignored for many dfiers, but some, like the List, will change their keys
    # accordingly, and some, like the Polymorph, produce very different graphs
    # with and without a value.
    #
    def sub_dfier_keys(self, value=None):
        return ()

    def sub_dfier(self, key, value=None):
        raise KeyError(key)

    def sub_value_keys(self, value):
        return ()

    def sub_value(self, value, key):
        raise KeyError(key)


class Anything(Dictifier):
    '''Dictifier for things like JSON dicts that are already dictified'''
    def dictify(self, value, **kwargs):
        return value

    def undictify(self, value, **kwargs):
        return value


class Field(Dictifier):
    '''Wrapper around a dictifier and an optional list of validators.

    A Field behaves like the dictifier handed to it on intialization, except in
    two respects:

    1. It handles None values
    2. It can have additional validators attached to it

    It passes None through dictify unchanged; on validation or undictifiance, it
    treats None as valid unless self.not_none is True, in which case it raises
    Invalid("empty")

    If a list of validators is passed on initialization, then field.validate()
    will call each validator in order and raise a NestedInvalid with all of
    their exceptions if any of them fail.
    '''
    def __init__(self, dfier, vdators=(), not_none=False):
        self.dfier = dfier
        self.vdators = tuple(vdators)
        self.not_none = not_none

    def dictify(self, value, **kwargs):
        if value is None:
            return None
        return self.dfier.dictify(value, **kwargs)

    def undictify(self, value, **kwargs):
        if value is None:
            # None is always valid when undictifying - the not_none flag only
            # applies when you validate the data.
            # TODO consider whether this is really desirable.
            return None
        return self.dfier.undictify(value, **kwargs)

    def validate(self, value, **kwargs):
        if value is None:
            if self.not_none:
                raise Invalid("empty")
            return
        fail_early = kwargs.get("dfy_fail_early", False)
        error_agg = ErrorAggregator(autoraise = fail_early)
        with error_agg.checking():
            self.dfier.validate(value)
        for vdator in self.vdators:
            with error_agg.checking():
                vdator.validate(value)
        error_agg.raise_if_any()

    @classmethod
    def asfield(cls, dfier):
        '''Wrap a dictifier in a Field if it isn't already one.'''
        if isinstance(dfier, Field):
            return dfier
        return Field(dfier)

    def sub_dfier_keys(self, value=None):
        return self.dfier.sub_dfier_keys(value)

    def sub_dfier(self, key, value=None):
        return self.dfier.sub_dfier(key, value)

    def sub_value_keys(self, value):
        return self.dfier.sub_value_keys(value)

    def sub_value(self, value, key, on_none='error'):
        if value is None:
            if on_none == 'error':
                raise KeyError(key)
            return None
        return self.dfier.sub_value(value, key)


def _doctest_field_tests():
    '''
    Empty function so I can write tests in doctest form.

    >>> from basic import Int
    >>> field = Field(Int())
    >>> field.dictify(None)
    >>> field.undictify(None)
    >>> field.validate(None)
    >>> req_field = Field(Int(), not_none=True)
    >>> req_field.dictify(None)
    >>> req_field.undictify(None)
    >>> req_field.validate(None)
    Traceback (most recent call last):
    ...
    Invalid: empty
    '''


if __name__ == '__main__':
    import doctest
    doctest.testmod()
