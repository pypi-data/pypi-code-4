class CashewException(Exception):
    pass

class InternalCashewException(CashewException):
    pass

class UserFeedback(CashewException):
    pass

class InactivePlugin(UserFeedback):
    def __init__(self, plugin_instance_or_alias):
        if isinstance(plugin_instance_or_alias, basestring):
            self.message = plugin_instance_or_alias
        else:
            self.message = plugin_instance_or_alias.alias

class NoPlugin(UserFeedback):
    pass
