from tw2.forms import SingleSelectField
from tw2.core import Deferred, CompoundWidget
from tw2.core import validation as vd
from tw2.forms import ListLayout
from datetime import datetime
from axf.dateformat import MONTHS

class DateMonthlySelectionField(ListLayout):
    month = SingleSelectField(label=None, prompt_text=None, validator=vd.Validator(required=True),
                              options=[(idx, MONTHS[idx]) for idx in range(1, 13)])
    year = SingleSelectField(label=None, prompt_text=None, validator=vd.Validator(required=True),
                             options=Deferred(lambda: range(1950, datetime.utcnow().year+1)))

    def prepare(self):
        super(CompoundWidget, self).prepare()

        if self.value:
            if not isinstance(self.value, dict):
                self.value = self.value.strip()
                self.value = datetime.strptime(self.value, '%Y-%m-%d')
                self.value = {'month': self.value.month,
                              'year': self.value.year}
        else:
            self.value = {}

        for c in self.children:
            if c.key in self.value:
                c.value = self.value[c.key]

        for c in self.children:
            c.prepare()

    @vd.catch_errors
    def _validate(self, value, state=None):
        self._validated = True
        value = value or {}
        if not isinstance(value, dict):
            raise vd.ValidationError('corrupt', self.validator, self)

        self.value = value
        any_errors = False
        data = {}
        for c in self.children:
            try:
                data[c.key] = c._validate(value[c.key], data)
            except vd.catch:
                data[c.key] = vd.Invalid
                any_errors = True

        data = '%(year)s-%(month)s-01' % data
        if self.validator:
            data = self.validator.to_python(data, state)

        if any_errors:
            raise vd.ValidationError('childerror', self.validator, self)

        return data
