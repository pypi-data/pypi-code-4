class PaymillError(Exception):
    """Paymill error.
    """

    pass


class AuthorizationError(PaymillError):
    """Authorization failed.
    """

    pass


class TransactionError(PaymillError):
    """Transaction error.
    """

    pass


class ServiceUnavailableError(PaymillError):
    """Paymill service is unavailable.
    """

    pass


class UnexpectedResponseError(PaymillError):
    """Paymill returned an unexpected response.
    """

    def __init__(self, message, error_json=None):
        super(UnexpectedResponseError, self).__init__(message)
        self.error_json = error_json


class ParseError(PaymillError):
    """Error parsing Paymill response data.
    """

    pass


class ResourceNotFoundError(PaymillError):
    """Resource not found.
    """

    pass


class RefundedAmountTooHighError(PaymillError):
    """Refunded amount is too high.
    """

    pass
