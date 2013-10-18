# -*- coding: utf-8 -*-

from tg import tmpl_context
from tw.api import WidgetsList
from tw.forms import TableForm, SingleSelectField, FormField, TextField
from tw.dynforms import OtherSingleSelectField, HidingContainerMixin, HidingSingleSelectField
from formencode import validators

class QuantityOtherSingleSelectField(HidingContainerMixin, FormField):
        template = "genshi:tw.dynforms.templates.other_select_field"

        params = {
        'field':        'The field on the object to use for the "other" text.',
        'other_code':   'The code used for "other"; occasionally you may need to override the default to avoid a clash with a valid value.',
        'other_text':   'The text string display for the "other" choice.',
        'specify_text': 'The text string display to prompt for a text value.',
        }

        other_code = -1
        other_text = 'Custom'
        specify_text = ''

        def __new__(cls, id=None, parent=None, children=[], **kw):
            children = [
                HidingSingleSelectField('select', mapping={kw.get('other_code', cls.other_code): ['other']}),            
                TextField('other'),
            ]
            return super(QuantityOtherSingleSelectField, cls).__new__(cls, id, parent, children, **kw)

        def __init__(self, *args, **kw):
            super(QuantityOtherSingleSelectField, self).__init__()

        def adapt_value(self, value):
            	return value

        def post_init(self, *args, **kw):
            self.validator = validators.NotEmpty

        def update_params(self, kw):
            options = ['1', '2', '5', '10', '20', '50', '100', '500', '1000']
            options.append((self.other_code, self.other_text))
            kw.setdefault('child_args', {})['select'] = {'options': options}
            return super(QuantityOtherSingleSelectField, self).update_params(kw)
