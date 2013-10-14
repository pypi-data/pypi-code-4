
""" ``checker`` module.
"""

from wheezy.validation.comp import __import__


class Checker(object):
    """ Intended to be used by unittest/doctest for validation rules.
        It is recommended to use test case per validator, test
        method per attribute, split by success check first than fails.
    """

    def __init__(self, stop=True, translations=None, gettext=None):
        """ Initialize validation checker.
        """
        self.stop = stop
        self.translations = translations
        self.gettext = gettext
        self.validator = None

    def use(self, validator):
        """ Use `validator` for next series of checks.
        """
        if isinstance(validator, str):
            namespace, name = validator.rsplit('.', 1)
            obj = __import__(namespace, None, None, [name])
            self.validator = getattr(obj, name)
        else:
            self.validator = validator

    def check(self, **kwargs):
        """ Returns a result of validation limited to attributes in
            `kwargs` which represents attributes of model being validated.
        """
        m = Model(dict.fromkeys([k for k, i in self.validator.rules] +
                                [k for k, i in self.validator.inner]))
        m.update(kwargs)
        results = {}
        self.validator.validate(m, results, self.stop,
                                self.translations, self.gettext)
        results = sorted([(k, results[k]) for k in kwargs if k in results])
        return results or None

    def error(self, **kwargs):
        """ Returns first error reported by validator.
        """
        results = self.check(**kwargs)
        return results and results[0][1][-1] or None

    def errors(self, **kwargs):
        """ Returns all errors reported by validator.
        """
        results = self.check(**kwargs)
        return results and results[0][1] or None


# region: internal details

class Model(dict):
    """ Simulate plain python class, read-only dictionary access
        through attributes.
    """
    __slots__ = ()

    def __getitem__(self, key):
        """ Returns `None` if key is missing.
        """
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            self[key] = None
            return None

    __getattr__ = __getitem__
