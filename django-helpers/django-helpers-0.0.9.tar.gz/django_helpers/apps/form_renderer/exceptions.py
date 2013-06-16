# coding=utf-8
from django.utils.translation import ugettext as _

class CSRFTokenMissingException(Exception):
    def __init__(self):
        Exception.__init__(self, _("Either request or csrf_token argument is needed."))


class FormIDMissingException(Exception):
    def __init__(self):
        Exception.__init__(self, _("Form ID is necessary"))
