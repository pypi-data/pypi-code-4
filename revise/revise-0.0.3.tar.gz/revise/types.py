from revise import errors
import uuid
import re


class TypeMeta(type):

    def __new__(cls, name, bases, attrs):
        klass = super(TypeMeta, cls).__new__(cls, name, bases, attrs)

        validators = []

        for attr_name, attr in attrs.iteritems():
            if attr_name.startswith("validate_"):
                validators.append(attr)

        setattr(klass, 'validators', validators)

        return klass


class BaseType(object):

    def __init__(self, name=None, default=None, required=None, *args,
                 **kwargs):
        self.name = name
        self.default = default
        self.required = bool(required)

        self._clean()

        # Validate that the default supplied value = A+

    def validate(self, value):

        if self._validated:
            return

        if value is None:
            if self.required:
                self._errors.append(errors.FieldRequired(self.name))
                return
            else:
                return

        if not self._coerced:
            try:
                value = self.to_python(value)
                self._coerced = True
                self.model.data[self.name] = value
            except errors.InvalidValue as e:
                self._errors.append(e)
                return

        for validator in self.validators:
            try:
                validator(self, value)
            except errors.InvalidValue as e:
                self._errors.append(e)
                # Check if error that stops process
                break

        self._validated = True

    def _clean(self):
        self._coerced = False
        self._validated = False
        self._errors = []

    @property
    def errors(self):
        return self._errors

    def to_python(self, value):
        pass

    def invalidate(self, message):
        raise errors.InvalidValue(self.name, message=message)

    __metaclass__ = TypeMeta


class String(BaseType):

    allow_casts = (int, str)

    def __init__(self, regex=None, min_length=None, max_length=None, *args,
                 **kwargs):
        super(String, self).__init__(*args, **kwargs)
        self.regex = regex
        if min_length and max_length and (min_length > max_length):
            raise ValueError(
                'The Minimum length is greater than the Maximum Length')
        self.min_length = min_length
        self.max_length = max_length

    def to_python(self, value):
        if value is None:
            return None
        if not isinstance(value, unicode):
            if isinstance(value, self.allow_casts):
                if not isinstance(value, str):
                    value = str(value)
                value = unicode(value, 'utf-8')
            else:
                self.invalidate("A valid string was not supplied")
        return value

    def validate_length(self, value):
        bounds = (bool(self.min_length), bool(self.max_length))
        if bounds == (False, False):
            return

        min_l = self.min_length or 0
        max_l = self.max_length or float('inf')

        MSG = {
            (True, True): ("Length must be between %s and %s characters"
                           % (min_l, max_l)),
            (True, False): "Length must be over %s characters" % min_l,
            (False, True): "Length must be less than %s characters" % max_l,
        }

        if not min_l <= len(value) <= max_l:
            if min_l == max_l:
                msg = "Length must be %s characters" % min_l
            else:
                msg = MSG.get(bounds)
            self.invalidate(msg)


class Number(BaseType):
    pass


class Decimal(BaseType):
    pass


class Boolean(BaseType):

    TRUE_VALUES = ('True', 'true', '1')
    FALSE_VALUES = ('False', 'false', '0')

    def to_python(self, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, basestring):
            if value in self.TRUE_VALUES:
                return True
            elif value in self.FALSE_VALUES:
                return False
        self.invalidate("A valid boolean was not supplied")


class DateTime(BaseType):
    pass


class Date(BaseType):
    pass


class Time(BaseType):
    pass


class Email(BaseType):
    pass


class UUID(BaseType):

    def to_python(self, value):
        try:
            return uuid.UUID(value)
        except ValueError:
            self.invalidate("A valid UUID was not provided.")


class HexHash(String):

    def to_python(self, value):
        value = super(HexHash, self).to_python(value)
        if not self.RE.match(value):
            self.invalidate("A valid hash was not provided")
        return value


class MD5(HexHash):
    RE = re.compile(r"^[a-fA-F\d]{32}$")


class SHA1(HexHash):
    RE = re.compile(r"^[a-fA-F\d]{40}$")


class SHA2(HexHash):
    RE = re.compile(r"^[a-fA-F\d]{64}$")


class SHA384(HexHash):
    RE = re.compile(r"^[a-fA-F\d]{96}$")


class SHA256(HexHash):
    RE = re.compile(r"^[a-fA-F\d]{128}$")


class SHA512(HexHash):
    RE = re.compile(r"^[a-fA-F\d]{256}$")


class List(BaseType):
    # contains
    # length
    # types
    # ? Think about this. Does a list has a place
    pass


class IPv4Address(BaseType):
    # turn subnets into address
    pass


class IPv4Network(BaseType):
    # turn subnets into address
    pass


class IPV6Address(BaseType):
    pass
    # turn subnets into address


class IPv6Network(BaseType):
    # turn subnets into address
    pass
