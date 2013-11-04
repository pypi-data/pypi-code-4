# coding=utf-8
from django.utils.translation import ugettext_lazy as _

from django.conf import settings as project_settings

CMSPLUGIN_CONTACT_FORMS = getattr(project_settings, "CMSPLUGIN_CONTACT_FORMS", (
        ('cmsplugin_question.forms.ContactForm', _('default')),
    )
)
