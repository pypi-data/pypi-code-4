from __future__ import absolute_import

from minos.validator import Validator
from minos.errors import ValidationError
import re

POSTAL_CODE_REGEX = re.compile(r"^\d{5}(-\d{4})?$")


class PostalCodeValidator(Validator):

    def validate(self, instance, *args, **kwargs):
        raise NotImplementedError

    #     key, = args
    #     value = getattr(instance, key)

    #     if "country_label" in kwargs:
    #         country_label = kwargs["country_label"]
    #         del kwargs["country_label"]
    #     else:
    #         country_label = getattr(instance, 'country').label

    #     self._validate(key, value, country_label, *args, **kwargs)

    # def _validate(self, key, value, country_label, *args, **kwargs):

    #     if not country_label or not value:
    #         return

    #     # zip codes get converted to ints by json_dt, except when they have a leading zero...
    #     value = unicode(value)

    #     if country_label == 'united_states' and not POSTAL_CODE_REGEX.match(value):
    #         raise ValidationError(key, value, 'Invalid Zip Code')

    #     if country_label == 'canada' and not re.match('[a-z][0-9][a-z][0-9][a-z][0-9]', value):
    #         raise ValidationError(key, value, 'Invalid Postal Code')

    #     # All other countries get a pass, for now
