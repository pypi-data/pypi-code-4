__all__ = [
    'Field',
    'ForeignKey',
    'NumberField',
    'StringField',
    'ObjectField',
    'DateTimeField',
    'ListField'
]

from datetime import datetime
import re

class Field(object):

    def __init__(self, required=False, default=None, alias='', extra=lambda x:True):
        self.alias = alias
        self.extra = extra
        self.required = required
        self.default = default

    def init(self, obj):
        obj[self.key] = self.default() if callable(self.default) else self.default

    def __get__(self, obj, owner):
        return obj.get(self.key, self.default)

    def __set__(self, obj, value):
        obj[self.key] = value

    def __delete__(self, obj):
        pass

    def set_key(self, key):
        self.key = self.alias or key

    def validate(self, obj):
        value = obj.get(self.key, None)

        if self.required and not value:
            return False

        return self.extra(value)


class OneToManyRelation(object):

    def __init__(self, connected_class, key):
        self.connected_class = connected_class
        self.key = key

    def __get__(self, obj, owner):
        return self.connected_class.Q.filter({self.key:obj['_id']}).fetch()

    def __set__(self, obj, value):
        pass

    def __delete__(self, obj):
        pass


class ForeignKey(Field):

    def __init__(self, related_model, relation_name='', **kwargs):
        super(ForeignKey, self).__init__(**kwargs)

        self.related_model = related_model
        self.relation_name = relation_name

    def __get__(self, obj, owner):
        rel_id = obj.get(self.key, 0)
        if rel_id:
            return self.related_model.Q.get(rel_id)

    def __set__(self, obj, value):
        if hasattr(value, 'id'):
            obj[self.key] = value.id

    def __delete__(self, obj):
        pass

    def install_relation(self, owner_class, class_name):
        relation_name = self.relation_name or ('%s_list' % class_name.lower())
        setattr(self.related_model, relation_name, OneToManyRelation(owner_class, self.key))


class NumberField(Field):

    def __init__(self, default=0, type=int, precision=0, constraints=(None, None), **kwargs):
        super(NumberField, self).__init__(**kwargs)

        self.type = type
        self.precision = precision
        self.constraints = constraints
        self.default = default

    def __get__(self, obj, owner):
        value = super(NumberField, self).__get__(obj, owner)

        if self.precision:
            value = round(value, self.precision)

        return self.type(value)

    def __set__(self, obj, value):
        obj[self.key] = self.type(value)

    def validate(self, obj):
        if super(NumberField, self).validate(obj):
            value = obj[self.key]
            _min, _max = self.constraints
            return ((_min == None) or (value >= _min)) and ((_max == None) or (value <= _max))
        else:
            return False


class StringField(Field):

    def __init__(self, pattern='', len_constraints=(None, None), **kwargs):
        super(StringField, self).__init__(**kwargs)

        self.pattern = re.compile(pattern)
        self.constraints = len_constraints

    def validate(self, obj):
        if super(StringField, self).validate(obj):
            value = obj[self.key]
            print 'pre RE match'
            print self.pattern.match(value)
            if self.pattern.match(value) is None:
                return False
            print 'RE match'
            _min, _max = self.constraints
            return ((_min == None) or (len(value) >= _min)) and ((_max == None) or (len(value) <= _max))
        else:
            return False


class ObjectField(Field):

    def __init__(self, default={}, **kwargs):
        super(ObjectField, self).__init__(**kwargs)

        self.default = dict(default)


class ListField(Field):

    def __init__(self, default=[], **kwargs):
        super(ObjectField, self).__init__(**kwargs)

        self.default = list(default)


class DateTimeField(Field):

    def __init__(self, default=datetime.now, constraints=(None, None), **kwargs):
        super(DateTimeField, self).__init__(**kwargs)

        self.constraints = constraints
        self.default = default

    def __set__(self, obj, value):
        if isinstance(value, int):
            obj[self.key] = datetime.fromtimestamp(value)
        elif isinstance(value, str):
            v = None
            for frmt in [
                    '%Y-%m-%dT%H:%M:%S.%f', # ISO 8601
                    '%Y-%m-%d %H:%M:%S.%f',
                    '%Y-%m-%dT%H:%M:%S',    # ISO 8601
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d'
                ]:
                try:
                    v = datetime.strptime(value, frmt)
                except:
                    pass

            if not v:
                raise Exception('Unknown datetime format DateTimeField.set()')

            obj[self.key] = v

        elif isinstance(value, datetime) or value is None:
            obj[self.key] = value
        else:
            raise Exception('Invalid type DateTimeField.set()')

    def validate(self, obj):
        if super(DateTimeField, self).validate(obj):
            value = obj[self.key]
            _min, _max = self.constraints
            return ((_min == None) or (value >= _min)) and ((_max == None) or (value <= _max))
        else:
            return False


