#coding=utf-8
import re

"""
ar must be an object of ActiveRecord or derived from it

ForeignKey(ar=Cafe)
TagStrip()
XssStrip()
Email()
Integer(op='<', arg=1500)
Integer()
Numeric()
Double(op='>', arg=15.0)
Double()
Required()
Length(op='>=', arg=100)
Trim()
Password()
Coords()
Unique(ar=Place, field='title')
Cast(op=cast_operator)
"""

class ValidationError(Exception):
    pass

class Security(object):
    name = ''
    value = None
    this = None
    errors = []
    
    pod = lambda x : not isinstance(x, type([])) and not isinstance(x, type({}))
    
    @property
    def val(self):
        return self.value
    
    def __init__(self, **kwargs):
        self.this = kwargs.get('this')
        
    def setvalue(self, v):
        self.value = v
    
    def setobject(self, o):
        self.this = o
    
    def perform(self):
        pass
    
    def __call__(self):
        self.errors = []
        return self.perform()
    
    def relop(self, reloper, source, target):
        
        if reloper == '<':
            return source < target
        elif reloper == '>':
            return source > target
        elif reloper == '=':
            return source == target
        elif reloper == '>=':
            return source >= target
        elif reloper == '<=':
            return source <= target
        
        return False
    
    def regex_match(self, regex):
        bad = 0
        if isinstance(self.value, type([])):
            for v in self.value:
                if not regex.match(v):
                    bad += 1
        elif isinstance(self.value, type({})):
            for v in self.value.itervalues():
                if not regex.match(v):
                    bad += 1
        else:
            if not regex.match(self.value):
                bad += 1
        
        return bad == 0
    
    errors_messages = {
        'fk':u'Элемент не найден',
        'double' :u'Параметр не является числом',
        'double_param':u'Значение должно быть %(relop)s %(arg)g',
        'email':u'Адрес электронной почты не корректен',
        'integer':u'Значение не является целым числом',
        'integer_param':u'Значение должно быть %(relop)s %(arg)d',
        'numeric':u'Значение не является числом',
        'required':u'Поле обязательно для заполнения',
        'password_length':u'Длина пароля короткая',
        'password_mismatch':u'Пароли не совпали',
        'length': u'Размер должен быть %(relop)s %(arg)d',
        'unique': u'Значение не может быть использовано',
        'coords_bad_range':u'Координаты заданы неверно',
        'photo': u'Изображение не загружено',
        'regex': u'Неверный формат'
    }
    def format_error(self, token, relop=None, arg=None):
        self.errors.append(self.errors_messages[token] % {'relop':relop,'arg':arg})

class ForeignKey(Security):
    name = 'fk'
    def __init__(self, **kwargs):
        super(ForeignKey, self).__init__(**kwargs)
        self.ar = kwargs.get('ar', None)
        
    def setobject(self, o):
        if not self.ar:
            self.ar = o.__class__
        super(ForeignKey, self).setobject(o)
    
    def is_number(self, num):
        return re.compile(r'^\d+$').match(num) != None
    
    def perform(self):
        
        if isinstance(self.value, type([])):
            new_value = []
            for v in self.value:                
                if not self.is_number(v) or int(v) != 0 and not self.ar.is_exists(int(v)):
                    new_value.append('0')
                else:
                    new_value.append(v)
            self.value = new_value
        elif isinstance(self.value, type({})):
            new_value = {}
            for k, v in self.value.iteritems():
                if not self.is_number(v) or int(v) != 0 and not self.ar.is_exists(int(v)):
                    new_value[k] = '0'
                else:
                    new_value[k] = v
                self.value = new_value
        else:
            if not self.is_number(self.value) or int(self.value) != 0 and not self.ar.is_exists(int(self.value)):
                self.value = '0'

        return True
        
        
class TagStrip(Security):
    name = 'tagstrip'
    def perform(self):
        regex_expr = '(\>|\<\/?)+'
        if isinstance(self.value, type([])):
            new_value = []
            for v in self.value:
                new_value.append(re.sub(regex_expr, '', v, re.I | re.M))
            self.value = new_value
        elif isinstance(self.value, type({})):
            new_value = {}
            for k, v in self.value.iteritems():
                new_value[k] = re.sub(regex_expr, '', v, re.I | re.M)
            self.value = new_value
        else:
            self.value = re.sub(regex_expr, '', self.value, re.I | re.M)
        
        return True
        
        
class XssStrip(Security):
    name = 'xssstrip'
    def perform(self):
        regex_expr = r'<(script|object|embed|iframe|applet|body|frameset|frame|head|html|form|vbscript)[^>]*?>(.*?)</\1>'
        if isinstance(self.value, type([])):
            new_value = []
            for v in self.value:
                new_value.append(re.sub(regex_expr, '', v, re.I | re.M | re.S))
            self.value = new_value
        elif isinstance(self.value, type({})):
            new_value = {}
            for k, v in self.value.iteritems():
                new_value[k] = re.sub(regex_expr, '', v, re.I | re.M | re.S)
            self.value = new_value
        else:
            self.value = re.sub(regex_expr, '', self.value, re.I | re.M | re.S)
        
        return True
    
    
class Email(Security):
    name = 'email'
    def perform(self):
        regex = re.compile('^([a-z0-9\+_\-]+)(\.[a-z0-9\+_\-]+)*@([a-z0-9\-]+\.)+[a-z]{2,6}$', re.I | re.U)
        result = self.regex_match(regex)
        
        if not result:
            self.format_error('email')
            
        return result
    
    
class Integer(Security):
    name = 'integer'
    def __init__(self, **kwargs):
        super(Integer, self).__init__(**kwargs)
        self.op = kwargs.get('op', None)
        self.arg = kwargs.get('arg', None)
        
    def perform(self):
        result = self.regex_match(re.compile(r'^[0-9]+$'))
        
        if not self.op and not self.arg and not result:
            self.format_error('integer')
        elif self.op and self.arg and not result:
            self.format_error('integer')
        if self.op and self.arg != None and result:
            bad = 0
            if isinstance(self.value, type([])):
                for v in self.value:
                    if not self.relop(self.op, int(v), self.arg):
                        bad += 1
                        self.format_error('integer_param', self.op, self.arg)
            elif isinstance(self.value, type({})):
                for v in self.value.values():
                    if not self.relop(self.op, int(v), self.arg):
                        bad += 1
                        self.format_error('integer_param', self.op, self.arg)
            else:
                if not self.relop(self.op, int(self.value), self.arg):
                    bad += 1
                    self.format_error('integer_param', self.op, self.arg)
            
            result = bad == 0
        
        return result
    
    
class Numeric(Security):
    name = 'numeric'
    def perform(self):
        result = self.regex_match(re.compile(r'^\d+|\d+\.\d+|\.\d+$'))
        
        if not result:
            self.format_error('numeric')
        
        return result
    
    
class Double(Security):
    name = 'float'
    def __init__(self, **kwargs):
        super(Double, self).__init__(**kwargs)
        self.op = kwargs.get('op', None)
        self.arg = kwargs.get('arg', None)
        
    def perform(self):
        result = self.regex_match(re.compile(r'^-?\d+|\d+\.\d+|\.\d+$'))
        
        if not self.op and not self.arg and not result:
            self.format_error('double')
        
        if self.op and self.arg and result:
            bad = 0
            if isinstance(self.value, type([])):
                for v in self.value:
                    if not self.relop(self.op, float(v), self.arg):
                        bad += 1
                        self.format_error('double_param', self.op, self.arg)
            elif isinstance(self.value, type({})):
                for v in self.value.values():
                    if not self.relop(self.op, float(v), self.arg):
                        bad += 1
                        self.format_error('double_param', self.op, self.arg)
            else:
                if not self.relop(self.op, float(self.value), self.arg):
                    bad += 1
                    self.format_error('double_param', self.op, self.arg)
            
            result = bad == 0
        
        return result
    
    
class Required(Security):
    name = 'required'
    def perform(self):
        
        bad = 0
        
        if isinstance(self.value, type([])):
            for v in self.value:
                bad += 1 if len(v) == 0 else 0
        elif isinstance(self.value, type({})):
            for v in self.value.values():
                bad += 1 if len(v) == 0 else 0
        else:
            bad += 1 if len(self.value) == 0 else 0
        
        if bad:
            self.format_error('required')
            
        return bad == 0
    
    
class Length(Security):
    name = 'length'
    def __init__(self, **kwargs):
        super(Length, self).__init__(**kwargs)
        self.op = kwargs.get('op')
        self.arg = kwargs.get('arg')
        
    def perform(self):
        bad = 0
        if isinstance(self.value, type([])):
            for v in self.value:
                if not self.relop(self.op, len(v), self.arg):
                    bad += 1
                    self.format_error('length', self.op, self.arg)
        elif isinstance(self.value, type({})):
            for v in self.value.itervalues():
                if not self.relop(self.op, len(v), self.arg):
                    bad += 1
                    self.format_error('length', self.op, self.arg)
        else:
            if not self.relop(self.op, len(self.value), self.arg):
                bad += 1
                self.format_error('length', self.op, self.arg)
        
        return bad == 0
    
    
class Trim(Security):
    name = 'trim'
    def perform(self):
        if isinstance(self.value, type([])):
            new_value = []
            for v in self.value:
                new_value.append(v.strip())
            self.value = new_value
        elif isinstance(self.value, type({})):
            new_value = {}
            for k, v in self.value.iteritems():
                new_value[k] = v.strip()
            self.value = new_value
        else:
            self.value = self.value.strip()
        
        return True
    
    
class Password(Security):
    name = 'password'
    def perform(self):
        if (isinstance(self.value, type([])) or isinstance(self.value, type({}))) and len(self.value) == 2:
            
            if isinstance(self.value, type([])):
                first, second = self.value[:2]
            else:
                first, second = list(self.value.values())[:2]
            if len(first) < 6:
                self.format_error('password_length')
                return False
            
            if first != second:
                self.format_error('password_mismatch')
                return False
            
            self.value = first
            
            return True
        
        self.format_error('password_mismatch')
        return False
    
    
class Coords(Security):
    name = 'coords'
    def perform(self):
        if isinstance(self.value, dict):
            self.value = self.value.values()
        
        if isinstance(self.value, list) and len(self.value) == 2:
            if not self.value[0] and not self.value[1]:
                return True
            
            val0 = float(self.value[0])
            val1 = float(self.value[1])
            
            if val0 <= 180.0 and val0 >= -180.0 and val1 <= 180.0 and val1 >= -180.0:
                self.value[0] = val0
                self.value[1] = val1
                return True
            
            self.format_error('coords_bad_range')
                
        return False
    
    
class Unique(Security):
    name = 'unique'
    def __init__(self, **kwargs):
        super(Unique, self).__init__(**kwargs)
        self.ar = kwargs.get('ar', None)
        self.field = kwargs.get('field')
        
    def setobject(self, o):
        if not self.ar:
            self.ar = o.__class__
        super(Unique, self).setobject(o)
        
    def perform(self):
        found = False
        cond = {}
        
        if self.this.has_key('_id'):
            cond = {'_id': {'$ne': self.this.get('_id')}}
        
        if isinstance(self.value, type([])):
            for v in self.value:
                cond[self.field] = v
                if self.ar.find_first(cond):
                    found = True
        elif isinstance(self.value, type({})):
            for v in self.value.itervalues():
                cond[self.field] = v
                if self.ar.find_first(cond):
                    found = True
        else:
            cond[self.field] = self.value
            if self.ar.find_first(cond):
                found = True
        
        if found:
            self.format_error('unique')
        
        return not found
    
    
class Cast(Security):
    def __init__(self, **kwargs):
        super(Cast, self).__init__(**kwargs)
        self.cast_oper = kwargs.get('op', None)
        
    def perform(self):
        
        self.value = self.performer(self.value)
        
        return True
        
    def performer(self, value):
        
        pod = lambda x : not isinstance(x, type([])) and not isinstance(x, type({}))
        
        if isinstance(value, type([])):
            new_value = []
            for v in value:
                new_value.append(self.cast_oper(v) if pod(v) else self.performer(v))
            return new_value
        elif isinstance(value, type({})):
            new_value = {}
            for k, v in value.iteritems():
                new_value[k] = self.cast_oper(v) if pod(v) else self.performer(v)
            return new_value
        else:
            return self.cast_oper(value.encode('ascii')) if value else 0

class Photo(Security):
    def __init__(self, **kwargs):
        super(Photo, self).__init__(**kwargs)
        self.required = kwargs.get('req', False)
        
    def perform(self):
        result = True
        
        for x in self.value.values():
            if x.has_key('hash') and x.has_key('ext'):
                if self.required and not x['hash'] and not x['ext']:
                    result = False
            else:
                result = False
        
        if not result:
            self.format_error('photo')
            
        return result

class Regex(Security):
    def __init__(self, arg):
        super(Regex, self).__init__()
        self.regex = arg
        
    def perform(self):
        ret = self.regex_match(re.compile(self.regex, re.UNICODE))
        if not ret:
            self.format_error('regex')
        return ret
