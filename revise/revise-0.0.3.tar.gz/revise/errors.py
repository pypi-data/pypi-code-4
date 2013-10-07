from collections import OrderedDict

__all__ = ('FieldRequired', 'InvalidValue', 'ValidationError')


class ValidationError(Exception):

    def __init__(self, field, resource=None, message=None):
        self.field = field
        self.resource = resource
        self.message = message

    @property
    def dict(self):
        d = OrderedDict({
            "field": self.field,
            "code": self.code
        })
        if self.resource:
            d['resource'] = self.resource
        if self.message:
            d['message'] = self.message
        return d


class FieldRequired(ValidationError):
    code = "required"


class InvalidValue(ValidationError):
    code = "invalid"
