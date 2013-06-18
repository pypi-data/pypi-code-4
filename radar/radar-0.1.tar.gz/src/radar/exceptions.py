__all__ = ('UnrecognisedDateFormat', 'InvalidDateRange')

class UnrecognisedDateFormat(ValueError):
    """
    Unrecognised date format.
    """
    pass

class InvalidDateRange(ValueError):
    """
    Invalid date range.
    """
    pass
