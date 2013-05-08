from .base import BaseError


class DataTypeError(BaseError):

    message = 'Invalid data type {value}. Must be dictionary.'


class UidFormatError(BaseError):

    message = 'Invalid uid "{value}". Must be contain only digits or must be integer.'
