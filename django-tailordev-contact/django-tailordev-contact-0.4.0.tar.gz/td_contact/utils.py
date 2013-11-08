# -*- coding: utf-8 -*-
from .settings import CONTACT_FORM_RULES


def get_rules_choices():
    """
    Format rules for a ChoiceField choices attribute
    """
    return [(k, v['subject']) for k, v in CONTACT_FORM_RULES.iteritems()]
