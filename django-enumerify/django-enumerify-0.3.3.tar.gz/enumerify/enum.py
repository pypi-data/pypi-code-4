from django.utils.translation import gettext as _

class Enum:
    """
        DESCRIPTION:
            To be used with models.IntegerField

        Enum.DEFAULT
            Is used to set the DEFAULT for all subclasses
            If the input == Enum.DEFAULT it will raise a validation error

            In order to create a DEFAULT (first choice option in html <select>) that is accepted as a valid select option
            You must override the value in the sub-class

        Enum.i18n
            Is used to set the visible value that is shown in the form
    """

    DEFAULT = 0

    i18n = (_('-'),)

    def __init__(self):
        # Check that it has valid keys
        # Check that it has valid values
        # Check that it can map to names - has the same amount of vars and
        if not len(self.get_keys()) > 0:
            raise Exception("Class '%s' must have at least one declared constant variable." % self.__class__.__name__)
        if not self.check_i18n():
            raise Exception("Class '%s' must have amount of variables as there are strings in 'i18n' tuple." % self.__class__.__name__)
        self.validate_values()

    def length(self):
        return len(self.get_keys())

    def check_i18n(self):
        if self.i18n:
            return len(self.i18n) == self.length()

    @classmethod
    def get_keys(cls):
        """
            DESCRIPTION:
                Get all variables that are spelled with CAPITALS and without double-underscores at head and tail.
        """
        return [key for key in cls.__dict__.iterkeys() if cls.is_valid_key(key)]

    @staticmethod
    def is_valid_key(value):
        # Filters and removes all the built-in variables starts and ends with double underscore
        return not value.startswith('__') and not value.endswith('__') and value.isupper()

    @classmethod
    def get_values(cls):
        return [cls.__dict__.get(key) for key in cls.get_keys()]

    @classmethod
    def get_sorted_values(cls):
        return sorted([cls.__dict__.get(key) for key in cls.get_keys()])


    @classmethod
    def get_as_tuple_list(cls):
        """
            DESCRIPTION: Returns an unsorted list of tuples formatted as [('VARIABLE1', 1), ...]
        """
        return [(key, cls.__dict__.get(key)) for key in cls.get_keys()]

    @classmethod
    def get_as_dict(cls):
        """
            DESCRIPTION: Returns an unsorted dict with class variables
        """
        items = {}
        for key, value in cls.get_as_tuple_list(): items[key] = value
        return items

    @classmethod
    def validate_values(cls, fail_silently=False):
        """
            DESCRIPTION:
                Check that all values defined are integers
                Overwrite this class for custom behavior
        """
        for value in cls.get_values():
            if not cls.is_valid_value(value):
                if fail_silently:
                    return False
                else:
                    raise ValueError("Value '%s' is not a valid integer." % value)

    @classmethod
    def is_in_keys(cls, value):
        """
            Check if class variable exists in class.
        """
        return value in cls.get_keys()

    @classmethod
    def is_in_values(cls, value):
        """
            DESCRIPTION:
                Check if value exists in a class variable.
                Can be used to validate if input from user is a valid input
        """
        return value in cls.get_values()

    @classmethod
    def choicify(cls):
        items = sorted(cls.get_as_tuple_list(), key=lambda item: item[1])
        return cls.prepend_default_first([(item[1], cls.i18n[index]) for index, item in enumerate(items)])

    @classmethod
    def get_dict(cls):
        return cls.__dict__

    @classmethod
    def prepend_default_first(cls, temp_list):
        if not cls.is_default_overridden():
            return [(Enum.DEFAULT, Enum.i18n[0])] + temp_list
        else:
            return temp_list

    @classmethod
    def is_default_overridden(cls):
        """
            Checks whether the sub-class has overwritten the DEFAULT key
        """
        return cls.is_in_keys('DEFAULT') or cls.is_in_values(0)

    @staticmethod
    def enumerify(items):
        if not isinstance(items, list):
            raise TypeError("List 'items' must be of type %s" % list().__class__)
        return [item for item in enumerate(items)]

    @staticmethod
    def is_valid_value(value):
        try:
            value = int(value)
            return True
        except TypeError:
            return False
        except ValueError:
            return False