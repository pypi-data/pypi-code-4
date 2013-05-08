class BaseError(Exception):

    message = None

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.message.format(value=self.value)


class DataTypeError(BaseError):

    message = 'Invalid data type {value}. Must be dictionary.'


class UidFormatError(BaseError):

    message = 'Invalid uid "{value}". Must be contain only digits or must be integer.'
