class CashewException(Exception):
    pass

class InternalCashewException(CashewException):
    pass

class UserFeedback(CashewException):
    pass

class InactivePlugin(UserFeedback):
    def __init__(self, plugin_instance):
        self.message = plugin_instance.alias

class NoPlugin(UserFeedback):
    pass
