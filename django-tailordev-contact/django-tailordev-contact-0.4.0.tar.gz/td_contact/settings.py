# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext as _


def format_managers_emails():
    """
    Format settings MANAGERS email as a recipient_list for the contact form
    """
    pattern = "%(name)s <%(email)s>"
    return [pattern % {'name': m[0], 'email': m[1]} for m in settings.MANAGERS]


# The default rule
CONTACT_FORM_DEFAULT_RULE = {
    'default': {
        'subject': _("General informations"),
        'to': format_managers_emails(),
        'prefix': _("[contact]"),
    }
}

# Rules
CONTACT_FORM_RULES = getattr(
    settings,
    'TD_CONTACT_FORM_RULES',
    CONTACT_FORM_DEFAULT_RULE
)

# Misc parameters
CONTACT_FORM_ALLOW_DIRECT_USER_CONTACT = getattr(
    settings,
    'TD_CONTACT_FORM_ALLOW_DIRECT_USER_CONTACT',
    False
)
