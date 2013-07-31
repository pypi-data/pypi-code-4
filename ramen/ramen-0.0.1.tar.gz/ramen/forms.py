#coding=utf-8
import re
import cgi
from ramen.models import ActiveRecord, ActiveRecordFactory
from ramen.rules import Rules

from settings import DB

class Form(object):

    def __init__(self, form_model, *args, **kwargs):
        self.form_model = form_model
        super(Form, self).__init__(*args, **kwargs)

    def _default_html_data(self):
        return {
            'tag': 'input',
            'class': '',
            'type': 'text',
            'value': '',
            'name': '',
            'name_suffix': '',
            'extra': '',
            'hint': '',
            'label': ''
        }

    def _create_html_tag(self, data={}, single=True):

        params = self._default_html_data()
        params.update(data)


        if hasattr(self.form_model, '_errors'):
            if data.get('name') in self.form_model._errors:
                params['class'] += ' error'
                params['hint'] = u'<br/>'.join(self.form_model._errors[data['name']])

        if single:
            return '<p class="%(class)s"><label>%(label)s<%(tag)s name="%(name)s%(name_suffix)s" type="%(type)s" value="%(value)s" %(extra)s/></label><span>%(hint)s</span></p>\n' % params
        else:
            return '<p class="%(class)s"><label>%(label)s<%(tag)s name="%(name)s%(name_suffix)s" %(extra)s>%(value)s</%(tag)s></label><span>%(hint)s</span></p>\n' % params

    def _guess_method(self, rules, value, default=None):
        tag = 'input'
        data = {}
        rules = rules[:]
        for rule in rules:
            if rule.name == 'fk':
                rule.setobject(self.form_model)
                data['collection'] = rule.ar.objects.all()
                data['collection'].load()
                data['display'] = 'admin_title'
                #if len(data['collection']) > 5:
                tag = 'select'
                if type(value) in [list, tuple]:
                    data['extra'] = 'multiple'

                #else:
                #    if type(value) in [list, tuple]:
                #        tag = 'checkgroup'
                #    else:
                #        tag = 'radiogroup'

                print 'ASDASD', data['collection']
                if not 'required' in [x.name for x in rules]: # and tag == 'select':
                    data['collection'].insert(0, {'_id':0, data['display']:'---'})

                print 'ASDASD', data['collection']

                if not (('required' in [x.name for x in rules]) or len(data['collection'])):
                    tag = 'input'
                    data = {}
                    data['type'] = 'hidden'
                    data['value'] = default

                rules.remove(rule)
            if rule.name == 'unique':
                rules.remove(rule)
        print tag, data, rules
        return tag, data, rules

    def render(self, exclude = []):
        s = []
        print 'RENDER'
        for r in self.form_model._rules:
            name, rules, d = (r + ('',))[:3]
            if name in exclude:
                continue
            tag_method, kwargs, rules = self._guess_method(rules, self.form_model.get(name, ''), d)
            if rules:
                kwargs['extra'] = cgi.escape('%s%s' % (kwargs.get('extra', ''), ' accept="%s"' % '|'.join([r.name for r in rules])))
            method = self.__getattribute__(tag_method)
            if isinstance(d, list) and tag_method in ['input', 'textarea']:
                vals = self.form_model.get(name, []) or d
                print 'V', vals
                for v in vals:
                    kwargs['value'] = v
                    kwargs['label'] = name
                    s.append(method(name = '%s[]' % name, **kwargs))
            elif isinstance(d, dict) and tag_method in ['input', 'textarea']:
                vals = self.form_model.get(name, {}) or d
                for k,v in vals.iteritems():
                    kwargs['value'] = v
                    kwargs['label'] = name
                    s.append(method(name = '%s[%s]' % (name, k), **kwargs))
            else:
                s.append(method(name = name, **kwargs))
        return ''.join(s)

    def input(self, name, type='text', hint='', extra='', value=None, label=''):
        return self._create_html_tag({
            'tag': 'input',
            'name': name,
            'type': type,
            'value': (value is not None) and str(value) or self.form_model.get(name, ''),
            'extra': extra,
            'hint': hint,
            'label': type == 'hidden' and ' ' or (label or name)
        })

    def textarea(self, name, hint='', extra='', value = None, label=''):
        return self._create_html_tag({
            'tag': 'textarea',
            'name': name,
            'value': (value is not None) and str(value) or self.form_model.get(name, ''),
            'extra': extra,
            'hint': hint,
            'label': label or name
        }, single=False)

    def select(self, name, options = [], collection = None, value='_id', display='_id', hint='', extra=''):
        if collection:
            options = [(obj[value], obj.get(display, ':(')) for obj in collection]
        _tmp = []
        multi = type(self.form_model.get(name, '')) in [list, tuple]
        for option in options:
            value, display = option
            if multi:
                selected = value in self.form_model.get(name, '') and 'selected' or ''
            else:
                selected = value == self.form_model.get(name, '') and 'selected' or ''
            _tmp.append('<option %s value="%s">%s</option>' % (selected, value, display))

        return self._create_html_tag({
            'tag': 'select',
            'name': name,
            'name_suffix': multi and '[]' or '',
            'extra': multi and 'multiple' or '',
            'value': ''.join(_tmp),
            'extra': extra,
            'hint': hint
        }, single=False)

    def radiogroup(self, name, options = [], collection = None, value='_id', display='_id', hint='', extra=''):
        print collection
        if collection:
            options = [(obj[value], obj.get(display, ':(')) for obj in collection]
        _tmp = []
        for option in options:
            value, display = option
            _tmp.append('<label><input type="radio" name="%s" value="%s" %s>%s</label>' % (name, value, value == self.form_model.get(name, '') and 'checked' or '', display, ))

        return self._create_html_tag({
            'tag': 'ul',
            'value': ''.join(_tmp),
            'extra': extra,
            'hint': hint
        }, single=False)

    def checkgroup(self, name, options = [], collection = None, value='_id', display='_id', hint='', extra=''):
        if collection:
            options = [(obj[value], obj[display]) for obj in collection]
        _tmp = []
        for option in options:
            value, display = option
            checked = (type(self.form_model.get(name, 0)) in [list, tuple] and value in self.form_model.get(name, [])) and 'checked' or ''
            _tmp.append('<label><input type="checkbox" name="%s[]" value="%s" %s>%s</label>' % (name, value, checked, display, ))

        return self._create_html_tag({
            'tag': 'ul',
            'value': ''.join(_tmp),
            'extra': extra,
            'hint': hint
        }, single=False)

    def submit(self, value='Submit', extra=''):
        return self._create_html_tag({
            'tag': 'input',
            'type': 'submit',
            'extra': extra,
            'value': value
        })

import sys
class FormModel(Rules):

    def __init__(self, *args, **kwargs):
        super(FormModel, self).__init__(*args, **kwargs)

    def is_valid(self, arguments):
        pod = lambda x : not isinstance(x, type([])) and not isinstance(x, type({}))
        self._errors = {}
        bad = 0
        for r in self._rules:
            k, rules, d = (r + ('',))[:3]

            try:
                value = arguments.get(k, False)
                if value == False:
                    continue

                if not value:
                    value = d

                err = self.validate(k, rules, value if pod(value) else value)
                if len(err) > 0:
                    bad += 1
                    self._errors[k] = err
            except Exception as e:
                print 'for key:', k, " Unexpected error:", sys.exc_info()[0], e
                raise

        #print self._errors
        return bad == 0

    def validate(self, k, rules, value):

        errors = []
        old_value = value

        for r in rules:
            r.setvalue(value)
            r.setobject(self)

            if not r():
                errors.extend(r.errors)

            value = r.val

        if len(errors):
            self[k] = old_value
        else:
            self[k] = value

        return errors

class ValidationError(Exception):
    pass


#class Security(object):
#    """Security - input data check"""
#    def __init__(self, rules, value):
#        self.rules = rules
#        self.value = value
#        self.errors = []
#
#    @property
#    def val(self):
#        return self.value
#
#    def perform(self):
#        """Выполнить проверку данных"""
#        regex = re.compile(r"^(fk|length|integer|double|unique)(\<|\>|\=|\>=|\<=)([a-z\.\_0-9\[\]\-]+)$")
#        bad = 0
#        for rule in self.rules:
#            if rule in ['xss_strip','email','integer','numeric','tag_strip','required','trim','double','password','coords']:
#                result = self.__getattribute__(rule)()
#            else:
#                m = regex.match(rule)
#                if m != None:
#                    result = self.__getattribute__(m.group(1))(op=m.group(2), arg=m.group(3))
#                else:
#                    raise ValidationError('Rule %s not found. May be in the future :)' % rule)
#
#            if not result:
#                bad += 1
#
#        return bad == 0
#
#    def xss_strip(self, **kwargs):
#        """вырезать небезопасные вставки HTML"""
#        regex_expr = r'<(script|object|embed|iframe|applet|body|frameset|frame|head|html|form|vbscript)[^>]*?>(.*?)</\1>'
#        if isinstance(self.value, type([])):
#            new_value = []
#            for v in self.value:
#                new_value.append(re.sub(regex_expr, '', v, re.I | re.M | re.S))
#            self.value = new_value
#        elif isinstance(self.value, type({})):
#            new_value = {}
#            for k, v in self.value.iteritems():
#                new_value[k] = re.sub(regex_expr, '', v, re.I | re.M | re.S)
#            self.value = new_value
#        else:
#            self.value = re.sub(regex_expr, '', self.value, re.I | re.M | re.S)
#
#        return True
#
#    def tag_strip(self, **kwargs):
#        """удалить теги"""
#        regex_expr = '(\>|\<\/?)+'
#        if isinstance(self.value, type([])):
#            new_value = []
#            for v in self.value:
#                new_value.append(re.sub(regex_expr, '', v, re.I | re.M))
#            self.value = new_value
#        elif isinstance(self.value, type({})):
#            new_value = {}
#            for k, v in self.value.iteritems():
#                new_value[k] = re.sub(regex_expr, '', v, re.I | re.M)
#            self.value = new_value
#        else:
#            self.value = re.sub(regex_expr, '', self.value, re.I | re.M)
#
#        return True
#
#    def email(self, **kwargs):
#        """проверить поле на соответствие почтовому ящику"""
#        regex = re.compile('^([a-z0-9\+_\-]+)(\.[a-z0-9\+_\-]+)*@([a-z0-9\-]+\.)+[a-z]{2,6}$', re.I | re.U)
#        result = self.regex_match(regex)
#
#        if not result:
#            self.format_error('email')
#
#        return result
#
#
#    def integer(self, op=None, arg=None):
#        """является ли поле целым числом с приведением"""
#        result = self.regex_match(re.compile('^[0-9]+$'))
#
#        if not op and not arg and not result:
#            self.format_error('integer')
#        elif op and arg and not result:
#            self.format_error('integer')
#        if op and arg and result:
#            bad = 0
#            if isinstance(self.value, type([])):
#                for v in self.value:
#                    if not self.relop(op, int(v), int(arg)):
#                        bad += 1
#                        self.format_error('integer_param', op, int(arg))
#            elif isinstance(self.value, type({})):
#                for k, v in self.value.iteritems():
#                    if not self.relop(op, int(v), int(arg)):
#                        bad += 1
#                        self.format_error('integer_param', op, int(arg))
#            else:
#                print op, int(self.value), arg
#                if not self.relop(op, int(self.value), int(arg)):
#                    bad += 1
#                    self.format_error('integer_param', op, int(arg))
#
#            result = bad == 0
#
#        if result:
#            if isinstance(self.value, type([])):
#                new_v = []
#                for v in self.value:
#                    new_v.append(int(v))
#                self.value = new_v
#            elif isinstance(self.value, type({})):
#                new_v = {}
#                for k, v in self.value.iteritems():
#                    new_v[k] = int(v)
#                self.value = new_v
#            else:
#                self.value = int(self.value)
#
#        return result
#
#    def numeric(self, **kwargs):
#        """проверить поле на принадлежность числу"""
#        result = self.regex_match(re.compile(r'^\d+|\d+\.\d+|\.\d+$'))
#
#        if not result:
#            self.format_error('numeric')
#
#        return result
#
#    def double(self, op=None, arg=None):
#        """число с плавающей точкой с приведением"""
#        result = self.regex_match(re.compile(r'^-?\d+|\d+\.\d+|\.\d+$'))
#
#        if not op and not arg and not result:
#            self.format_error('double')
#
#        if op and arg and result:
#            bad = 0
#            if isinstance(self.value, type([])):
#                for v in self.value:
#                    if not self.relop(op, float(v), float(arg)):
#                        bad += 1
#                        self.format_error('double_param', op, float(arg))
#            elif isinstance(self.value, type({})):
#                for k, v in self.value.iteritems():
#                    if not self.relop(op, float(v), float(arg)):
#                        bad += 1
#                        self.format_error('double_param', op, float(arg))
#            else:
#                if not self.relop(op, float(self.value), float(arg)):
#                    bad += 1
#                    self.format_error('double_param', op, float(arg))
#
#            result = bad == 0
#
#        if result:
#            if isinstance(self.value, type([])):
#                new_v = []
#                for v in self.value:
#                    new_v.append(float(v))
#                self.value = new_v
#            elif isinstance(self.value, type({})):
#                new_v = {}
#                for k, v in self.value.iteritems():
#                    new_v[k] = float(v)
#                self.value = new_v
#            else:
#                self.value = float(self.value)
#
#        return result
#
#
#    def fk(self, op, arg):
#        """вторичный ключ для коллекции"""
#        AR = ActiveRecordFactory(arg)
#        print AR
#        bad = 0
#        assert len(self.value)
#        print 'V', self.value, type(self.value)
#        if isinstance(self.value, type([])):
#            for v in self.value:
#                if int(v) != 0 and not AR.is_exists(v):
#                    bad += 1
#                    self.format_error('fk')
#        elif isinstance(self.value, type({})):
#            for k, v in self.value.iteritems():
#                if int(v) != 0 and not AR.is_exists(v):
#                    bad += 1
#                    self.format_error('fk')
#        else:
#            # ar = AR(self.value)
#            if int(self.value) != 0 and not AR.is_exists(self.value):
#                bad += 1
#                self.format_error('fk')
#
#        return bad == 0
#
#    def required(self, **kwargs):
#        """обязательно существование значения"""
#        l = len(self.value)
#
#        if l == 0:
#            self.format_error('required')
#
#        return l > 0
#
#    def length(self, op, arg):
#        bad = 0
#        if isinstance(self.value, type([])):
#            for v in self.value:
#                if not self.relop(op, len(v), int(arg)):
#                    bad += 1
#                    self.format_error('length', op, int(arg))
#        elif isinstance(self.value, type({})):
#            for k, v in self.value.iteritems():
#                if not self.relop(op, len(v), int(arg)):
#                    bad += 1
#                    self.format_error('length', op, int(arg))
#        else:
#            if not self.relop(op, len(self.value), int(arg)):
#                bad += 1
#                self.format_error('length', op, int(arg))
#
#        return bad == 0
#
#    def trim(self, **kwargs):
#        """удалить пробельные символы в начале и конце строки"""
#        if isinstance(self.value, type([])):
#            new_value = []
#            for v in self.value:
#                new_value.append(v.strip())
#            self.value = new_value
#        elif isinstance(self.value, type({})):
#            new_value = {}
#            for k, v in self.value.iteritems():
#                new_value[k] = v.strip()
#            self.value = new_value
#        else:
#            self.value = self.value.strip()
#
#        return True
#
#    def password(self):
#        """пароль, значением должен быть список с двумя элементами"""
#        if isinstance(self.value, type([])) and self.value.len() == 2:
#            if len(self.value[0]) < 6:
#                self.format_error('password_length')
#                return False
#
#            if self.value[0] != self.value[1]:
#                self.format_error('password_mismatch')
#                return False
#
#            self.value = self.value[1]
#
#            return True
#
#        return False
#
#    def coords(self):
#        """географические координаты"""
#        if isinstance(self.value, list) and len(self.value) == 2:
#            if not self.value[0] and not self.value[1]:
#                return True
#
#            val0 = float(self.value[0])
#            val1 = float(self.value[1])
#
#            if val0 <= 180.0 and val0 >= -180.0 and val1 <= 180.0 and val1 >= -180.0:
#                self.value[0] = val0
#                self.value[1] = val1
#                return True
#
#            self.format_error('coords_bad_range')
#
#        return False
#
#    def unique(self, op, arg):
#        """проверить уникальность значения для данного поля в коллекции"""
#        m = re.match('^([a-z0-9\_]+)\[([a-z0-9\_]+)\]$', arg)
#        if not m:
#            raise ValidationError('Invalid rule syntax for <unique=collection[field]>')
#
#        db = DB
#        coll = db._db[m.group(1)]
#        field = m.group(2)
#        found = False
#        if isinstance(self.value, type([])):
#            for v in self.value:
#                if coll.find_one({field:v}):
#                    found = True
#        elif isinstance(self.value, type({})):
#            for k, v in self.value.iteritems():
#                if coll.find_one({field:v}):
#                    found = True
#        else:
#            if coll.find_one({field:self.value}):
#                found = True
#
#        if found:
#            self.format_error('unique')
#
#        return not found
#
#    def relop(self, reloper, source, target):
#        if reloper == '<':
#            return source < target
#        elif reloper == '>':
#            return source > target
#        elif reloper == '=':
#            return source == target
#        elif reloper == '>=':
#            return source >= target
#        elif reloper == '<=':
#            return source <= target
#
#        return False
#
#    def regex_match(self, regex):
#        bad = 0
#        if isinstance(self.value, type([])):
#            for v in self.value:
#                if not regex.match(v):
#                    bad += 1
#        elif isinstance(self.value, type({})):
#            for k, v in self.value.iteritems():
#                if not regex.match(v):
#                    bad += 1
#        else:
#            if not regex.match(self.value):
#                bad += 1
#
#        return bad == 0
#
#    errors_messages = {
#        'fk':u'Элемент не найден',
#        'double' :u'Параметр не является числом',
#        'double_param':u'Значение должно быть %(relop)s %(arg)g',
#        'email':u'Адрес электронной почты не корректен',
#        'integer':u'Значение не является целым числом',
#        'integer_param':u'Значение должно быть %(relop)s %(arg)d',
#        'numeric':u'Значение не является числом',
#        'required':u'Поле обязательно для заполнения',
#        'password_length':u'Длина пароля короткая',
#        'password_mismatch':u'Пароли не совпали',
#        'length': u'Размер должен быть %(relop)s %(arg)d',
#        'unique': u'Значение не может быть использовано',
#        'coords_bad_range':u'Координаты заданы неверно'
#    }
#    def format_error(self, token, relop=None, arg=None):
#        self.errors.append(self.errors_messages[token] % {'relop':relop,'arg':arg})
#
#
