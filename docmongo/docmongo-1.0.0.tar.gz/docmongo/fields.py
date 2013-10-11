from abc import ABCMeta
import datetime


class BaseField(metaclass=ABCMeta):
    """this class is abstract

    Attributes:
        value: storage value
    """
    kind = None

    def __init__(self, initial_word):
        self.value = initial_word

    def validate(self):
        """ check type"""
        if self.value is not None and not isinstance(self.value, self.kind):
            raise TypeError("{0} is not {1}".format(self.value, self.kind))
        return True

    def s(self, value):
        """ set"""
        self.value = value

    def g(self):
        """ get"""
        return self.value

    # virtual method
    def get_init_value(self):
        if self.value is None:
            if callable(self.kind):
                return self.kind()
            return None
        return self.value


class StringField(BaseField):
    kind = str

    def __init__(self, initial_word=None):
        super().__init__(initial_word)


class IntField(BaseField):
    kind = int

    def __init__(self, initial_word=None):
        super().__init__(initial_word)


class DictField(BaseField):
    kind = dict

    def __init__(self, initial_word=None):
        if initial_word is None:
            initial_word = self.kind()
        super().__init__(initial_word)

    def __setitem__(self, key, value):
        self.value[key] = value

    def __getitem__(self, key):
        return self.value.get(key)

    def __getattr__(self, key):
        return getattr(self.value, key)

    def __len__(self):
        return len(self.value)

    def __contains__(self, item):
        return item in self.value

    def __add__(self, other):
        self.value.update(other)
        return self

    def __iter__(self):
        return iter(self.value)


class ListField(BaseField):
    kind = list

    def __init__(self, initial_word=None):
        if initial_word is None:
            initial_word = self.kind()
        super().__init__(initial_word)

    def __setitem__(self, key, value):
        self.value[key] = value

    def __getitem__(self, key):
        return self.value[key]

    def __getattr__(self, key):
        return getattr(self.value, key)

    def __len__(self):
        return len(self.value)

    def __contains__(self, item):
        return item in self.value

    def __add__(self, other):
        if not isinstance(other, list):
            other = [other]
        self.value += other
        return self

    def __iter__(self):
        return iter(self.value)


class DateField(BaseField):
    kind = datetime.datetime

    def __init__(self, initial_date=None, now=False):
        if now:
            initial_date = datetime.datetime.now()
        super().__init__(initial_date)

    def get_init_value(self):
        return self.kind.now()


class AnyField(BaseField):
    kind = object

    def __init__(self, initial_word=None):
        super().__init__(initial_word)

    def get_init_value(self):
        return None


def field_to_object(value):
    """ primary value convert object of inherited BaseField"""
    mapping = {
        str: StringField,
        int: IntField,
        list: ListField,
        dict: DictField,
        datetime.datetime: DateField,
    }
    return mapping.get(type(value), AnyField)(value)
