# -*- coding: utf-8 -*-

from nose.tools.trivial import (assert_equals, assert_true, assert_false)

from valhalla import Schema

test_data = {
    'valid_visa': ('4012888888881881', '12.2020', '124'),
    'valid_amex': ('378282246310005', '09-2020', '9090'),
    'valid_mc': ('5105105105105100', '120', '123'),
    'valid_discover': ('6011000990139424', '120', '123'),
    'valid_other': ('30569309025904', '920', '123'),
    'invalid_number': ('6011000990139429', '920', '123'),
    'invalid_date': ('30569309025904', '12-06-1989', '124'),
    'invalid_csc': ('378282246310005', '120', '123'),
    'forbidden_type': ('378282246310005', '09-2020', '9090'),
    'expired_date': ('378282246310005', '0689', '9090')
}


def test_credit_card():
    s = Schema()

    s.valid_visa.credit_card()
    s.valid_amex.credit_card()
    s.valid_mc.credit_card()
    s.valid_discover.credit_card()
    s.valid_other.credit_card()
    s.invalid_number.credit_card()
    s.invalid_date.credit_card()
    s.invalid_csc.credit_card()
    s.forbidden_type.credit_card(brands=['visa'])
    s.expired_date.credit_card()

    s.validate(test_data)
    assert_false(s.valid)

    assert_true(s.valid_visa.valid)
    assert_true(s.valid_amex.valid)
    assert_true(s.valid_mc.valid)
    assert_true(s.valid_discover.valid)
    assert_true(s.valid_other.valid)
    assert_false(s.invalid_number.valid)
    assert_false(s.invalid_date.valid)
    assert_false(s.invalid_csc.valid)
    assert_false(s.forbidden_type.valid)
    assert_false(s.expired_date.valid)

    assert_equals(s.valid_visa.result[3], u'visa')
    assert_equals(s.valid_amex.result[3], u'amex')
    assert_equals(s.valid_mc.result[3], u'mastercard')
    assert_equals(s.valid_discover.result[3], u'discover')
    assert_equals(s.valid_other.result[3], u'other')

    assert_equals(s.invalid_number.errors[
                  0], 'The specified credit card number is not valid.')
    assert_equals(s.invalid_date.errors[
                  0], 'Invalid expiration date format. Must be one of : [MMYY, MYY, MYYYY, MMYYYY]')
    assert_equals(s.invalid_csc.errors[0], 'The CSC code is not valid.')
    assert_equals(s.forbidden_type.errors[
                  0], 'The type amex is not an acceptable brand.')
    assert_equals(s.expired_date.errors[0], 'The credit card is expired.')
