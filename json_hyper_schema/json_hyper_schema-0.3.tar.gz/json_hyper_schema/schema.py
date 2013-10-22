"""
Implementation of json schema draft 03

http://tools.ietf.org/html/draft-zyp-json-schema-03
"""
import re
import datetime
import hashlib
import urlparse
import json

from collections import defaultdict

import iso8601
from validate_email import validate_email
import ipaddress

from json_reference import Reference


class SchemaNotFound(Exception):
    pass


class ValidationError(Exception):
    """
    Error raised when validation fails
    """
    def __init__(self, errors=None):
        if errors is None:
            errors = {}

        if not isinstance(errors, dict):
            errors = {'/': [errors]}

        self.errors = errors

        super(ValidationError, self).__init__()

    @property
    def message(self):
        return json.dumps(self.errors)

    def append(self, error, prefix=''):
        if not isinstance(error, ValidationError):
            raise TypeError('Only ValidationErrors can be appended')
        
        for pointer, errors in error.errors.items():
            if prefix:
                pointer = '/%s%s' % (prefix, pointer)
                
            if pointer not in self.errors:
                self.errors[pointer] = []

            self.errors[pointer] += errors

    def __str__(self):
        return self.message


class Schema(dict):
    """
    Representation of a json schema
    """
    type_map = {
        'string': (unicode, str),
        'number': (float, int, long),
        'integer': (int, long),
        'boolean': bool,
        'object': dict,
        'array': list,
        'null': None.__class__
    }

    def __init__(self, data, base_url=None):
        """
        Initialize a schema

        Expands `$ref` in schema's if a schema is registered
        Replaces the apropriate fields with sub schema's

        :params data: the schema data
        """
        if not base_url:
            base_url = 'http://%s' % hashlib.md5(json.dumps(data)).hexdigest()
            Reference.register(base_url, data)

        if 'id' in data:
            base_url = urlparse.urljoin(base_url, data['id'])

        self.base_url = base_url
        
        super(Schema, self).__init__(data)

        try:
            reference = Reference(data['$ref'], self.base_url)
            self.__init__(
                reference.get(),
                base_url=urlparse.urljoin(self.base_url, data['$ref'])
            )
        except KeyError:
            pass

    def validate(self, data):
        """
        Validate `data` against the schema

        :params data: data to validate
        :raises ValidationError: If the data did not validate
        """
        error = ValidationError()

        for func in [func for func in dir(self) if
                     func.startswith('_validate_')]:
            try:
                value = self.get(func.replace('_validate_', ''), None)
                getattr(self, func)(data, value)
            except ValidationError, e:
                error.append(e)
                
        if error.errors:
            raise error

    def links(self, data):
        """
        Property containing the links specified in the schema

        :returns: a dict with the relation names as indexes and the links as values

        Also adds the arguments of the href for convienance
        """
        def fill_template(link):
            if 'schema' in link:
                link['schema'] = Schema(link['schema'], self.base_url)

            try:
                link['href'] = link['href'].format(**data)
            except KeyError:
                pass
            
            return link

        return [
            fill_template(link) for link in self.get('links', {})
        ]

    @property
    def example(self):
        """
        Example data for the schema

        :returns: An example of a string that conforms the schema
        """
        if 'properties' in self:
            return dict(
                (prop, sub_schema.example) for prop, sub_schema in
                self['properties'].items()
            )

        elif 'items' in self:
            return [
                self['items'].example,
                self['items'].example,
                '...'
            ]
        elif 'enum' in self:
            return '(%s)' % ('|'.join(self['enum']))
        elif 'description' in self and 'type' in self:
            return '<%s:%s>' % (self['type'], self['description'])

        elif 'title' in self and 'type' in self:
            return '<%s:%s>' % (self['type'], self['title'])

        elif 'type' in self:
            return '<%s>' % (self['type'], )

        else:
            return '<...>'

    def _validate_extends(self, data, extends):
        """
        Validate data against the "extends" property of the current schema:

        The value of this property MUST be another schema which will provide
        a base schema which the current schema will inherit from.  The
        inheritance rules are such that any instance that is valid according
        to the current schema MUST be valid according to the referenced
        schema.  This MAY also be an array, in which case, the instance MUST
        be valid for all the schemas in the array.  A schema that extends
        another schema MAY define additional attributes, constrain existing
        attributes, or add other constraints.

        Conceptually, the behavior of extends can be seen as validating an
        instance against all constraints in the extending schema as well as
        the extended schema(s).  More optimized implementations that merge
        schemas are possible, but are not required.  An example of using
        "extends":

        {
            "description":"An adult",
            "properties":{"age":{"minimum": 21}},
            "extends":"person"
        }



        {
            "description":"Extended schema",
            "properties":{"deprecated":{"type": "boolean"}},
            "extends":"http://json-schema.org/draft-03/schema"
        }
        """
        if not extends:
            return

        if isinstance(extends, list):
            for sub_schema in extends:
                self._validate_extends(data, sub_schema)
        else:
            schema = Schema(extends, self.base_url)
            schema.validate(data)

    def _validate_required(self, data, required):
        """
        Validate data against the "required" property of the current schema:

        This attribute indicates if the instance must have a value, and not
        be undefined.  This is false by default, making the instance
        optional.
        """
        for property, sub_schema in self.get('properties', {}).items():
            if sub_schema.get('required') and property not in data:
                raise ValidationError('Missing required field: %s' % property)

    def _validate_properties(self, data, properties):
        """
        Validate data against the "properties" property of the current schema:

        This attribute is an object with property definitions that define the
        valid values of instance object property values.  When the instance
        value is an object, the property values of the instance object MUST
        conform to the property definitions in this object.  In this object,
        each property definition's value MUST be a schema, and the property's
        name MUST be the name of the instance property that it defines.  The
        instance property value MUST be valid according to the schema from
        the property definition.  Properties are considered unordered, the
        order of the instance properties MAY be in any order.
        """
        if data is None or properties is None:
            return

        error = ValidationError()

        if not isinstance(data, dict):
            return
        
        for property, sub_schema in properties.items():
            try:
                Schema(sub_schema, self.base_url).validate(data[property])
            except KeyError:
                pass
            except ValidationError, e:
                error.append(e, property)

        if error.errors:
            raise error
            
    def __validate_additional_property(self, value, additional_properties):
        """
        Validate data against the "additionalProperties" property of the current schema:

        This provides a definition for additional properties in an array instance
        when tuple definitions of the properties is provided.  This can be false
        to indicate additional properties in the array are not allowed, or it can
        be a schema that defines the schema of the additional properties.
        """
        if additional_properties is None:
            return

        if additional_properties is False:
            raise ValidationError('Additional properties not allowed')
        
        if isinstance(additional_properties, dict):
            sub_schema = Schema(additional_properties, self.base_url)
            sub_schema.validate(value)

    def _validate_patternProperties(self, data, pattern_properties):
        """
        Validate data against the "patternProperties" property of the current schema:
        """
        if pattern_properties is None:
            pattern_properties = {}

        if not isinstance(data, dict):
            return

        for property, value in data.items():
            matched = False
            for pattern, sub_schema in pattern_properties.items():
                if re.findall(pattern, property):
                    matched = True
                    Schema(sub_schema, self.base_url).validate(value)

            if not matched and property not in self.get('properties', {}):
                self.__validate_additional_property(
                    data[property],
                    self.get('additionalProperties')
                )
                                        
    def _validate_items(self, data, items):
        """
        Validate data against the "items" property of the current schema:

        This attribute defines the allowed items in an instance array, and
        MUST be a schema or an array of schemas.  The default value is an
        empty schema which allows any value for items in the instance array.

        When this attribute value is a schema and the instance value is an
        array, then all the items in the array MUST be valid according to the
        schema.

        When this attribute value is an array of schemas and the instance
        value is an array, each position in the instance array MUST conform
        to the schema in the corresponding position for this array.  This
        called tuple typing.  When tuple typing is used, additional items are
        allowed, disallowed, or constrained by the "additionalItems"
        (Section 5.6) attribute using the same rules as
        "additionalProperties" (Section 5.4) for objects.
        """
        if data is None or items is None or not isinstance(data, list):
            return

        try:
            items = self['items']
        except KeyError:
            return

        if not isinstance(data, list):
            raise ValidationError(
                'Should be a list'
            )
        error = ValidationError()

        if isinstance(items, list):
            for index, item in enumerate(data):
                try:
                    Schema(items[index], self.base_url).validate(item)
                except IndexError:
                    self.__validate_additional_item(
                        item, self.get('additionalItems')
                    )
                except ValidationError, e:
                    error.append(e, str(index))

        if isinstance(items, dict):
            sub_schema = Schema(items, self.base_url)
            for index, item in enumerate(data):
                try:
                    sub_schema.validate(item)
                except ValidationError, e:
                    error.append(e, str(index))

        if error.errors:
            raise error

    def _validate_type(self, data, type):
        """
        Validate data against the "type" property of the current schema:

        This attribute defines what the primitive type or the schema of the
        instance MUST be in order to validate.  This attribute can take one
        of two forms:

        Simple Types  A string indicating a primitive or simple type.  The
        following are acceptable string values:

         * string  Value MUST be a string.

         * number  Value MUST be a number, floating point numbers are
        allowed.

         * integer  Value MUST be an integer, no floating point numbers are
        allowed.  This is a subset of the number type.

         * boolean  Value MUST be a boolean.

         * object  Value MUST be an object.

         * array  Value MUST be an array.

         * null  Value MUST be null.  Note this is mainly for purpose of
         being able use union types to define nullability.  If this type
         is not included in a union, null values are not allowed (the
         primitives listed above do not allow nulls on their own).
         
         * any  Value MAY be of any type including null.

        If the property is not defined or is not in this list, then any
        type of value is acceptable.  Other type values MAY be used for
        custom purposes, but minimal validators of the specification
        implementation can allow any instance value on unknown type
        values.

        Union Types

        An array of two or more simple type definitions.  Each
        item in the array MUST be a simple type definition or a schema.
        The instance value is valid if it is of the same type as one of
        the simple type definitions, or valid by one of the schemas, in
        the array.

        For example, a schema that defines if an instance can be a string or
        a number would be:

        {"type":["string","number"]}
        """
        if type == 'any' or type is None:
            return

        if isinstance(type, dict):
            sub_schema = Schema(type, self.base_url)
            sub_schema.validate(data)
            return
        
        if isinstance(type, list):
            for item in type:
                try:
                    self._validate_type(data, item)
                    return
                except ValidationError:
                    pass

            raise ValidationError(
                'Not of type %s' % type
            )

        if data is None and type != 'null':
            raise ValidationError(
                'Not of type %s' % type
            )

        if not isinstance(data, self.type_map[type]):
            raise ValidationError(
                'Not of type %s' % type
            )

        if isinstance(data, bool) and type in ('integer', 'number'):
            raise ValidationError(
                'Not of type %s' % type
            )

    def _validate_disallow(self, data, disallow):
        if disallow is None:
            return
        
        try:
            self._validate_type(data, disallow)
        except ValidationError:
            return

        raise ValidationError('%s is not allowed' % disallow)

    def _skip_validate_patternProperties(self, data, pattern_properties):
        """
        Validate data against the "patternProperties" property of the current schema:

        This attribute is an object that defines the schema for a set of
        property names of an object instance.  The name of each property of
        this attribute's object is a regular expression pattern in the ECMA
        262/Perl 5 format, while the value is a schema.  If the pattern
        matches the name of a property on the instance object, the value of
        the instance's property MUST be valid against the pattern name's
        schema value.
        """
        if pattern_properties is None:
            return

        if not isinstance(data, dict):
            raise ValidationError(
                'Should be a dictionary' % (data,)
            )

        for pattern, sub_schema in pattern_properties.items():
            pattern = re.compile(pattern)

            properties = dict(
                [(property, sub_schema) for property in data
                 if pattern.match(property)]
            )

            self._validate_properties(data, properties)

    def __validate_additional_item(self, item, additional_items):
        """
        Validate data against the "additionalItems" property of the current schema:

        This provides a definition for additional items in an array instance
        when tuple definitions of the items is provided.  This can be false
        to indicate additional items in the array are not allowed, or it can
        be a schema that defines the schema of the additional items.
        """
        if additional_items is None:
            return

        if additional_items is False:
            raise ValidationError('Additional items not allowed')

        if isinstance(additional_items, dict):
            sub_schema = Schema(additional_items, self.base_url)
            sub_schema.validate(item)

    def _validate_dependencies(self, data, dependencies):
        """
        Validate data against the "dependencies" property of the current schema:

        This attribute is an object that defines the requirements of a
        property on an instance object.  If an object instance has a property
        with the same name as a property in this attribute's object, then the
        instance must be valid against the attribute's property value
        (hereafter referred to as the "dependency value").

        The dependency value can take one of two forms:

        Simple Dependency

        If the dependency value is a string, then the
        instance object MUST have a property with the same name as the
        dependency value.  If the dependency value is an array of strings,
        then the instance object MUST have a property with the same name
        as each string in the dependency value's array.

        Schema Dependency

        If the dependency value is a schema, then the
        instance object MUST be valid against the schema.
        """
        if not dependencies:
            return
        
        if not isinstance(data, dict):
            return

        for property in data:
            try:
                dependency = dependencies[property]
                if isinstance(dependency, (str, unicode)):
                    if not data.get(dependency):
                        raise ValidationError('Missing dependency: %s' % dependency)
                elif isinstance(dependency, list):
                    for dep in dependency:
                        self._validate_dependencies(data, {property: dep})
                else:
                    Schema(dependency, self.base_url).validate(data)
            except KeyError:
                pass

    def _validate_minimum(self, data, minimum):
        """
        Validate data against the "minimum" property of the current schema:

        This attribute defines the minimum value of the instance property
        when the type of the instance value is a number.
        """
        if minimum is None:
            return

        if not isinstance(data, (int, float)):
            return

        if self.get('exclusiveMinimum', False):
            if data <= minimum:
                raise ValidationError(
                    'Should be smaller then %s' % minimum
                )
        else:
            if data < minimum:
                raise ValidationError(
                    'Should be smaller (or equal) then %s' % minimum
                )

    def _validate_maximum(self, data, maximum):
        if maximum is None:
            return

        if not isinstance(data, (int, float)):
            return
        
        if self.get('exclusiveMaximum', False):
            if data >= maximum:
                raise ValidationError(
                    'Should be smaller then %s' % maximum
                )
        else:
            if data > maximum:
                raise ValidationError(
                    'Should be smaller (or equal) then %s' % maximum
                )

    def _validate_minItems(self, data, min_items):
        if min_items is None:
            return

        if not isinstance(data, list):
            return

        if len(data) < min_items:
            raise ValidationError(
                'Should be longer then %s' % min_items
            )

    def _validate_maxItems(self, data, max_items):
        if max_items is None:
            return

        if not isinstance(data, list):
            return

        if len(data) > max_items:
            raise ValidationError(
                'Should be shorter then %s' % max_items
            )

    def _validate_uniqueItems(self, data, uniqueItems):
        if uniqueItems is None:
            return
        
        if not isinstance(data, list):
            return

        if not uniqueItems:
            return
        
        if any(data.count(x) > 1 for x in data):
            raise ValidationError(
                'Items should be unique' % data
            )

    def _validate_pattern(self, data, pattern):
        if pattern is None:
            return

        if not isinstance(data, (str, unicode)):
            return

        regex = re.compile(pattern)

        if not regex.match(data):
            raise ValidationError(
                'Does not match %s' % pattern
                )

    def _validate_minLength(self, data, min_length):
        if min_length is None:
            return

        if not isinstance(data, (str, unicode)):
            return

        if len(data) < min_length:
            raise ValidationError(
                'Should be longer then %s' % min_length
            )

    def _validate_maxLength(self, data, max_length):
        if max_length is None:
            return

        if not isinstance(data, (str, unicode)):
            return

        if len(data) > max_length:
            raise ValidationError(
                'Should be shorter then %s' % max_length
            )

    def _validate_divisibleBy(self, data, divisible_by):
        if divisible_by is None:
            return

        if not isinstance(data, (int, float)):
            return

        if data / float(divisible_by) != int(data / float(divisible_by)):
            raise ValidationError(
                'Should be divisible by %s' % divisible_by
                )

    def _validate_enum(self, data, enum):
        if enum is None:
            return

        if data not in enum:
            raise ValidationError('Is not in %s' % self['enum'])

    def _validate_format(self, data, format):
        if format is None:
            return

        try:
            try:
                self._validate_type(data, 'string')
            except ValidationError:
                raise ValidationError('Is not a valid %s' % format)

            getattr(
                self,
                '_format_%s' % (format.replace('-', '_'), )
            )(data)
        except AttributeError, e:
            raise NotImplemented(
                'format %s is not implemented' % (format, )
            )

    def _format_date_time(self, data):
        try:
            iso8601.parse_date(
                data,
                "%Y-%m-%dT%H:%M:%S.%f.m%Z"
            )
        except iso8601.ParseError:
            raise ValidationError('Is not a valid date-time')

    def _format_date(self, data):
        try:
            datetime.datetime.strptime(
                data,
                "%Y-%m-%d"
            )
        except ValueError:
            raise ValidationError('Is not a valid date')

    def _format_time(self, data):
        try:
            datetime.datetime.strptime(
                data,
                '%H:%M:%S'
                )
        except ValueError:
            raise ValidationError('Is not a valid time')

    def _format_utc_milisec(self, data):
        try:
            int(data)
        except ValueError:
            raise ValidationError('Is not a valid utc-milisec')

    def _format_regex(self, data):
        try:
            re.compile(data)
        except:
            raise ValidationError('Is not a valid regex')

    def _format_color(self, data):
        if data in ['aqua', 'black', 'blue', 'fuchsia', 'gray', 'green', 'lime',
                    'maroon', 'navy', 'olive', 'purple', 'red', 'silver', 'teal',
                    'white', 'yellow', 'orange']:
            return

        if not re.match('^\#(A|B|C|D|E|F|0-9)+', data):
            raise ValidationError('Is not a valid color')

    def _format_email(self, data):
        if not validate_email(data):
            raise ValidationError('Is not a valid email')
   
    def _format_uri(self, data):
        try:
            parsed = urlparse.urlparse(data)
            if not parsed.scheme:
                raise ValidationError('Is not a valid uri')
        except ValueError:
            raise ValidationError('Is not a valid uri')

    def _format_ip_address(self, data):
        try:
            adr = ipaddress.ip_address(unicode(data))
            if not isinstance(adr, ipaddress.IPv4Address):
                raise ValueError('Found IPv6 address')
        except ValueError:
            raise ValidationError('Is not a valid ip-address')

    def _format_ipv6(self, data):
        try:
            adr = ipaddress.ip_address(unicode(data))
            if not isinstance(adr, ipaddress.IPv6Address):
                raise ValueError('Found IPv4 address')
        except ValueError:
            raise ValidationError('Is not a valid IPv6-address')

    def _format_host_name(self, data):
        if len(data) > 255:
            raise ValidationError('Is not a valid hostname')
        
        if data[-1] == ".":
            data = data[:-1]  # strip exactly one dot from the right, if present
        
        allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)

        if not all(allowed.match(x) for x in data.split(".")):
            raise ValidationError('Is not a valid hostname')
