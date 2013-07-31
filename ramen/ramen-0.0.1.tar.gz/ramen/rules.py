

class Rules(dict):
    _rules = ()
    _errors = {}
    _lang = ''

    def collect_rules(self, cls):
        for b in cls.__bases__:
            if hasattr(b, '_rules'):
                self._rules = b._rules + self._rules
                self.collect_rules(b)

    def __init__(self, *args, **kwargs):
        super(Rules, self).__init__(*args, **kwargs)
        self.collect_rules(self.__class__)        
        for r in self._rules:
            name, rule, default = (r + ('',))[:3]
            self[name] = callable(default) and default() or type(default)(default)

    @property
    def errors(self):
        return self._errors

    def __setattr__(self, attr, value):
        if attr in self:
            self[attr] = value
        else:
            object.__setattr__(self, attr, value)

    def __getattr__(self, attr):
        if attr in self:
            if self._lang and isinstance(self[attr], dict):
                return self[attr][self._lang]
            else:
                if isinstance(self[attr], str):
                    return self[attr].decode('utf-8')
                else:
                    return self[attr]
        else:
            return object.__getattribute__(self, attr)
