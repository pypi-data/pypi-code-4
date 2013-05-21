class AwsError(Exception):
    """Base error class."""
    pass


class AwsRequestFailureError(AwsError):
    """A packaged request was met with an unexpected response."""
    pass
