# -*- coding: utf-8 -*-
# system
import re

# framework
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


identifier_re = re.compile(r"[a-z0-9A-Z:_+\-\|/]+$", re.UNICODE)


def validate_setting_name(name):
    if not identifier_re.match(name):
        msg = _("Given name '%s' contains characters that may "
                "cause errors with some caching backends" % name)
        raise ValidationError(msg)
