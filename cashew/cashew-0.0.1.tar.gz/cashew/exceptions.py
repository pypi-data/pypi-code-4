class CashewException(Exception):
    pass

class InternalCashewException(CashewException):
    pass

class UserFeedback(CashewException):
    pass

class InactivePlugin(UserFeedback):
    pass

class NoPlugin(UserFeedback):
    pass
