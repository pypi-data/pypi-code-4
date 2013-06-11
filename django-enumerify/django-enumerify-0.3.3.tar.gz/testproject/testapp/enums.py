# -*- coding: utf-8 -*-

from django.utils.translation import gettext as _

from enumerify.enum import Enum

class ExamStatus(Enum):
    FAIL = 0
    PASS = 1

    i18n = (
        _('Fail'),
        _('Pass')
    )