from __future__ import absolute_import

from minos.errors import ValidationError
from minos.validator import Validator


class PhoneValidator(Validator):

    def validate(self, instance, *args, **kwargs):
        #Not implemented
        raise NotImplementedError

#     #     key, = args
#     #     value = getattr(instance, key)

#     #     self._validate(key, value, country, instance_name, *args, **kwargs)

#     # def _validate(self, key, value, country, instance_name="", *args, **kwargs):
#     #     import phonenumbers  # Not installed on science boxes.

#     #     error = ValidationError(key, value, "Invalid phone number.")

#     #     if not value:
#     #         return  # Not a presence validator

#     #     if not country:
#     #         raise TypeError("Country cannot be '{}' when trying "
#     #             "to validate instance {}'s '{}'='{}'. Check this user's "
#     #             "data.".format(country, instance_name, key, value))
#     #     elif not country.telephone_code:
#     #         raise TypeError("%s's telephone code cannot be None when trying to validate '%s'='%s'" %
#     #                 (country, key, value))

#     #     value = unicode(value)
#     #     if not value.isdigit():
#     #         raise error

#     #     try:
#     #         # Unfortunately, the way we store countries and the way
#     #         # phonenumbers create Number object are incompatible. We have to
#     #         # parse it. It is rather inexpensive.
#     #         number = phonenumbers.parse(country.telephone_code + value)
#     #     except phonenumbers.NumberParseException:
#     #         raise error

#     #     # phonenumbers also provides is_valid_number which also checks if the
#     #     # number is valid according to the numbering plan. Unfortunately, this
#     #     # raised a number of possible false positives, so we're only using
#     #     # is_possible_number which just checks the number length.
#     #     if not phonenumbers.is_possible_number(number):
#     #         raise error

#     #     if country.iso3 == "USA" and value[0] in ("0", "1"):
#     #         # Additionnal checking for the USA
#     #         raise error