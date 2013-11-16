from django import forms


class ChecksumError(forms.ValidationError):
    def __init__(self, expected, got, code=None, params=None):
        message = (
            'Form checksum not valid. Expected {expected}, but got {got}'
            .format(expected=expected, got=got)
        )
        super.__init__(message, code, params)
