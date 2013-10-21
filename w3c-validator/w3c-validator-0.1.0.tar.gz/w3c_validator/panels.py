import re
import requests
from StringIO import StringIO

from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from w3c_validator.validator import Validator


from debug_toolbar.panels import DebugPanel


class W3CValidatorDebugPanel(DebugPanel):
    name = "W3C Validation"
    has_content = True

    log_data = None
    errors_count = 0
    warns_count = 0
    src_content = ''

    def nav_title(self):
        return _("W3C Validator")

    def nav_subtitle(self):
        return mark_safe(_(u"Errors: %(errors_cnt)d "\
                           u"Warnings: %(warns_cnt)d") % {
            'errors_cnt': self.errors_count,
            'warns_cnt': self.warns_count,
            })

    def title(self):
        return _("W3C Validator")

    def url(self):
        return ''

    def process_response(self, request, response):
        self.validator = Validator()
        self.validator.validate_source(response.content)
        self.src = response.content.split("\n")
        self.errors_count = self.validator.error_count
        self.warns_count = self.validator.warning_count
        return response

    def appearance(self, errors):
        replacements = [
            (re.compile(r'\<([^\>]*)\>'), \
                '<strong class="code">&lt;\\1&gt;</strong>'),
            (re.compile(r'(line[^\-]*)(.*)'), \
                u'<td><pre class="handle-position">\\1</pre></td><td class="tidy-msg">\\2<td>'),
            (re.compile(r'\s*\-\s+(Error\:|Warning\:)', re.I), \
                        u'<i>\\1</i>'),
        ]

        for rx, rp in replacements:
            errors = re.sub(rx, rp, errors)

        errors_list = errors.split('\n')
        errors_rt = []
        # mark lines with error with validation-error class
        for err in errors_list:
            if 'error:' in err.lower():
                err = err.replace('<td>', '<td class="validation-error">')
                errors_rt.append(err)
                continue
            errors_rt.append(err)

        return errors_rt

    def content(self):
        context = self.context.copy()
        context.update({
        'validator': self.validator,
        })

        return render_to_string('w3c_validator/panel.html', context)
