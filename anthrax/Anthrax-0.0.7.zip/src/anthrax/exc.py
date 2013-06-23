class ValidationError(BaseException):
    def __init__(self, message, suggestions=None):
        self.message = message
        self.suggestions = suggestions

    def __repr__(self):
        return '<{0}>'.format(self.message)
    __str__ = __repr__

class FormValidationError(ValidationError):
    def __init__(self, fields, message):
        self.fields = fields
        super(FormValidationError, self).__init__(message, None)
