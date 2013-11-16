import re
from django import forms
from buysafe.widgets import NumberTextInput


class NumberStringField(forms.CharField):
    """
    A CharField subclass that contains only numbers. This is different with
    IntegerField because NumberStringField can have leading zeros. Usaful for
    Things like telephone numbers
    """
    widget = NumberTextInput

    def validate(self, value):
        super(NumberStringField, self).validate(value)
        if re.match(r'^\d*$', value) is None:
            raise forms.ValidationError(
                'This field should only consist numbers'
            )


class SunTechChecksumField(forms.CharField):
    def validate(self, value):
        super(SunTechChecksumField, self).validate(value)
        if re.match(r'^[0-9A-F]{40}$', value) is None:
            raise forms.ValidationError(
                'Checksum should be of length 40, and consists only numbers '
                'and/or capital alphabets from A through F.'
            )
