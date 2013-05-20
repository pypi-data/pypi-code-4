"""Settings for the ``multilingual_orgs`` app."""
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


display_type_choices = [
    ('small', _('small')),
    ('big', _('big')),
]

DISPLAY_TYPE_CHOICES = getattr(
    settings, 'ORGANIZATION_PLUGIN_DISPLAY_TYPE_CHOICES', display_type_choices)
