__version__ = '0.1.1'


class DoesntMatch(AssertionError):
    pass


class Matcher(object):

    def __init__(self, condition):
        self.condition = condition

    def __eq__(self, other):
        return self.condition(other)

    def __ne__(self, other):
        try:
            return not self.condition(other)
        except DoesntMatch:
            return True

    def __and__(self, other):
        if not isinstance(other, Matcher):
            other = Matcher(other)
        return self.__class__(lambda ob: self.condition(ob) and
                              other.condition(ob))

    def __or__(self, other):
        if not isinstance(other, Matcher):
            other = Matcher(other)

        def orcondition(ob):
            try:
                if other.condition(ob):
                    return True
            except DoesntMatch:
                return self.condition(ob)

        return self.__class__(orcondition)


def HasKeysAndAttrs(**attrs):

    attrs = attrs.copy()

    has_attrs = attrs.pop('has_attrs', [])
    has_keys = attrs.pop('has_keys', [])
    has_items = dict(attrs.pop('has_items', []))

    has_keys.extend(has_items.keys())
    has_attrs.extend(attrs.keys())

    def match_func(other):
        marker = []

        for item in has_keys:
            if item not in other:
                raise DoesntMatch('%r does not contain the key %r' %
                                  (other, item))

        for item in has_attrs:
            if getattr(other, item, marker) is marker:
                raise DoesntMatch('%r does not have an attribute '
                                  'named %r. ' % (other, item))

        for item, expected in attrs.items():
            value = getattr(other, item)
            if expected != value:
                raise DoesntMatch('%r.%s: Expected %r. Got %r.' %
                                  (other, item, expected, value))

        for key, expected in has_items.items():
            value = other[key]
            if expected != value:
                raise DoesntMatch('%r[%r]: Expected %r. Got %r.' %
                                  (other, key, expected, value))

        return True
    return Matcher(match_func)


def InstanceOf(cls, **attrs):
    def match_func(other):
        if not isinstance(other, cls):
            raise DoesntMatch('Expected: %s instance. '
                              'Got: %r' % (cls, other))
        return True
    return Matcher(match_func) & HasKeysAndAttrs(**attrs)


def Contains(*things):
    """
    Return a matcher that matches only if all ``things`` are present in the
    object
    """
    return Matcher(lambda container: all(n in container for n in things))


def DoesntContain(*things):
    """
    Return a matcher that matches only if none of ``things`` is present in the
    object
    """
    return Matcher(lambda container: all(n not in container for n in things))


def Anything(**attrs):
    return Matcher(lambda other: True) & HasKeysAndAttrs(**attrs)


def DictLike(*args, **kwargs):
    return HasKeysAndAttrs(has_items=dict(*args, **kwargs))
