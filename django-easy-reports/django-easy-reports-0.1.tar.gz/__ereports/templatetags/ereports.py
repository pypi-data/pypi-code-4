# -*- coding: utf-8 -*-
import datetime
from decimal import Decimal, InvalidOperation
from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import BooleanField
from django.db.models.fields.related import ForeignKey
from django.template.base import Template
from django.template.defaultfilters import floatformat, date
import pprint
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe
from kiowa.utils import get_attr as recursive_getattr


register = template.Library()


def _get_field(Model, field_path):
    """
    get a Model and a path to a attribute, return the field


    >>> a = _get_field(Payslip, 'contract.employee.health_ins_type')
    >>> print a
    Health Insurance Type
    """
    parts = field_path.split('.')
    target = parts[0]
    if target in Model._meta.get_all_field_names():
        field_object, model, direct, m2m = Model._meta.get_field_by_name(target)
        if isinstance(field_object, models.fields.related.ForeignKey):
            if parts[1:]:
                return _get_field(field_object.rel.to, '.'.join(parts[1:]))
            else:
                return field_object
        else:
            return field_object
    return None


@register.simple_tag
def header(model, field_name):
    field = _get_field(model, field_name)
    if field and hasattr(field, 'verbose_name'):
        label = field.verbose_name
    elif '|' in field_name:
        name, __ = field_name.split('|')
        label = name.replace('.', ' ').replace('_', ' ').title()
    else:
        label = field_name.replace('.', ' ').replace('_', ' ').title()
    return smart_str(label)


@register.simple_tag(takes_context=True, name='cell')
def process_queryset_field(context, obj, field_name, raw=False):
    context['current_row'] = obj
    if raw:
        if '|' in field_name:
            field_name, __ = field_name.split('|')
        if '#' in field_name:
            field_name, __ = field_name.split('|')

        attr = recursive_getattr(obj, field_name)
        Field = _get_field(obj.__class__, field_name)
        if callable(attr):
            return attr()
        elif issubclass(Field.__class__, BooleanField):
            return {True:'yes', False:'no'}[attr]
        return attr
    else:
        if field_name.startswith('{'):
            pattern = "{%% load ereports %%}%s" % field_name
        elif '|' in field_name:
            pattern = "{%% load ereports %%}{{current_row.%s}}" % field_name
        else:
            pattern = "{%% load ereports %%}{{current_row.%s}}" % field_name

        t = Template(pattern)
        value = t.render(context)
        return value or '&nbsp;'

@register.filter()
def currency(dollars):
    dollars = round(float(dollars), 2)
    return "%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])


def isNumeric(s):
    try:
        return int(s) or True
    except (ValueError, TypeError):
        pass
    try:
        Decimal(s) or True
    except (ValueError, TypeError, InvalidOperation):
        pass
    try:
        return float(s) or True
    except (ValueError, TypeError):
        pass
    return False


@register.simple_tag
def formatvalue(value):
    if isinstance(value, (Decimal, float)):
        ret = "<div class='currency'>%s</div>" % currency(value)
    elif isinstance(value, (int,)):
        ret = "<div class='int'>%s</div>" % value
    elif isinstance(value, (datetime.datetime, datetime.date)):
        ret = "<div class='date nobr'>%s</div>" % date(value, 'd b Y')
    elif isinstance(value, basestring) and isNumeric(value):
        ret = "<div class='numeric'>%s</div>" % value
    elif value is None or unicode(value).strip() == '':
        ret = '&nbsp;'
    else:
        ret = value
    return mark_safe(ret)

@register.filter(name='formatvalue')
def formatvalue_filter(value):
    return formatvalue(value)

@register.filter(name='formatvalue')
def formatvalue_filter(value):
    return mark_safe(formatvalue(value))


@register.filter('str')
def _str(target):
    return str(target)


@register.filter('int')
def _int(target):
    return int(target)


@register.filter('float')
def _float(target):
    return float(target)


@register.simple_tag
def field_link(owner, field):
    if owner:
        label = '%s.%s' % (owner, field.name)
    else:
        label = field.name

    args = {'class': 'field',
            'label': label,
            'title': '',
            'owner': None}

    if isinstance(field, ForeignKey):
        opts = field.rel.to._meta
        args.update({'class': 'inspect closed field',
                     'title': reverse('get_model_meta', args=[label, opts.app_label, opts.object_name.lower()])})
    return '<div class="%(class)s" title="%(title)s">%(label)s</div>' % args


@register.simple_tag(takes_context=True)
def make_total(context, value, var_name):
    var = var_name[1:]
    if var_name[0] == '+':
        partial = context.get(var, 0)
        partial = partial + value
        context[var] = partial
        return floatformat(value, 2)
    elif var_name[0] == '=':
        return floatformat(context[var], 2)


@register.simple_tag(takes_context=True)
def qs(context, varname, default=None):
    filter_target = context['request'].GET.get(varname, default)
    return filter_target


@register.simple_tag(takes_context=True)
def edebug(context):
    ret = {}
    for i in context:
        for k, v in i.items():
            if k not in ['request', 'LANGUAGES', 'sql_queries', 'headers',
                         'STATIC_URL', 'LANGUAGE_BIDI', 'LANGUAGE_CODE',
                         'csrf_token', 'session_cookie_alert',
                         'session_cookie_age_fmt',
                         'session_cookie_expire_fmt',
                         'session_cookie_age',
                         'uitheme', 'kiowamedia', 'browser', ]:
                ret[k] = v

                #    ret.append('%s: %s' % (k, str(context[k])))

    return pprint.pformat(ret)


@register.filter
def running_total(qs, fieldname):
    values = [recursive_getattr(d, fieldname) for d in qs]

    def is_summable(value):
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    return sum(map(float, filter(is_summable, values)))


@register.filter
def payroll_total(qs, fieldname):
    values = [recursive_getattr(d, fieldname) for d in qs]
    try:
        return formatvalue(sum(map(float, values)))
    except (ValueError, TypeError):
        return ''


@register.filter
def currencyformat(value, thousand_sep=',', decimal_sep='.'):
    """
    Returns the currency format of the value param using specified separators

    Usage: {% value_to_format|currencyformat %}
    """
    integer_part_string = str(int(value))
    f = lambda x, y, list=[]: f(x[:-y], y, [(x[-y:])] + list) if x else list
    integer_part = thousand_sep.join(f(integer_part_string, 3))
    return "%s%s%s" % (integer_part, decimal_sep, ("%0.2f" % value)[-2:])


@register.simple_tag
def summarize(group, fieldname):
    return formatvalue(group.sum(fieldname))


@register.simple_tag(name='get_attr')
def get_attr_tag(target, attrname):
    return recursive_getattr(target, attrname)


@register.simple_tag
def get_formatted_value(target, attrname):
    return formatvalue(recursive_getattr(target, attrname))


@register.simple_tag
def astoday(object, method_name):
    m = recursive_getattr(object, method_name)
    return m(datetime.date.today())


@register.filter
def div_mod(dividend, divisor):
    quotient, remainder = divmod(dividend, divisor)
    return quotient, remainder


@register.filter
def yes_no(value):
    return {True: 'Yes', False: 'No', None: 'N/A'}.get(value, 'N/A')

