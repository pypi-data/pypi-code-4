# -*- coding: utf-8 -*-

from datetime import datetime, date
from re import compile as re_compile, sub

from valhalla import ValidationError


def _enum(**enums):
    return type('Enum', (), dict(enums.items() + {'items': enums}.items()))


def _explode_int(number):
    return [int(n) for n in str(number)]

_CC_REGEX = _enum(
    VISA=re_compile(r'^4\d{12}(\d{3})?$'),
    MASTERCARD=re_compile(r'^(5[1-5]\d{4}|677189)\d{10}$'),
    AMEX=re_compile(r'^3[47]\d{13}$'),
    DISCOVER=re_compile(r'^(6011|65\d{2})\d{12}$')
)

_CC_TYPE = _enum(
    VISA=u'visa',
    MASTERCARD=u'mastercard',
    AMEX=u'amex',
    DISCOVER=u'discover',
    OTHER=u'other'
)

# accepts a tuple (number, exp_date, csc), returns (long(number),
# date_obj, int(csc), CC_TYPE)


def credit_card(brands=[], _value=(), *args, **kwargs):
    if type(_value) is not tuple:
        raise ValidationError(
            'This validator requires a (number, exp_date, csc) tuple.')

    def _detect_brand(number):
        for t, regex in _CC_REGEX.items.iteritems():
            if regex.match(number):
                return _CC_TYPE.items[t]

        return _CC_TYPE.OTHER

    def _luhn_test(number):
        digits = _explode_int(number)
        # Hehe, yeah.
        return True if not sum(digits[-1::-2] + [sum(_explode_int(n * 2)) for n in digits[-2::-2]]) % 10 else False

    def _mk_date(exp_date):
        exp_date = sub(r'[-/\.\s]', '', exp_date)
        format_dict = {
            4: '%m%y',
            6: '%m%Y'
        }

        if len(exp_date) in (3, 5):
            exp_date = u'0' + exp_date

        try:
            date_format = format_dict[len(exp_date)]
        except KeyError:
            raise ValidationError(
                'Invalid expiration date format. Must be one of : [MMYY, MYY, MYYYY, MMYYYY]')

        return datetime.strptime(exp_date, date_format).date()

    number, exp_date, csc = _value
    if not _luhn_test(number):
        raise ValidationError('The specified credit card number is not valid.')

    cc_type = _detect_brand(number)
    if brands and cc_type not in brands:
        raise ValidationError(
            'The type %s is not an acceptable brand.' % (cc_type))

    exp_date = _mk_date(exp_date)
    if exp_date < date.today():
        raise ValidationError('The credit card is expired.')

    if (cc_type == _CC_TYPE.AMEX and len(csc) != 4) or (cc_type != _CC_TYPE.AMEX and len(csc) != 3):
        raise ValidationError('The CSC code is not valid.')

    return (long(number), exp_date, int(csc), cc_type)
