"""
generators.py

Contains the different builtin generators as well as the Generator abstract
class.

@author RNDuldulao, Jr.
@version 0.1a_dev2

"""
import abc
import random
import sys
import datetime


import rstr


class Generator:
    """Abstract class for value generators."""
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    @abc.abstractmethod
    def generate(self, *args, **kwargs):
        """Subclasses must implement this method."""
        raise NotImplementedError()

class Constant(Generator):
    """Returns a constant value."""
    def __init__(self, value=''):
        self.value = value

    def generate(self, *args, **kwargs):
        """Return value."""
        return self.value

class Int(Generator):
    """Random int generator from min to max and generates using the
       format parameter as outputspec.
    """
    
    def __init__(self, minimum = 0, maximum=0, format='%d'):
        """Constructor.
        """
        self.minimum = minimum
        self.format = format
        if not maximum or maximum < minimum:
            self.maximum = sys.maxint
        else:
            self.maximum = maximum

    def generate(self, *args, **kwargs):
        """Generate random int, returns string using format spec."""
        return self.format % random.randint(self.minimum, self.maximum)

class IntID(Generator):
    """A sequential integer generator.  The generate method returns
       start up to N in step increments.
       
    """
    def __init__(self, start=0, step=1):
        """Constructor"""
        self.start = start
        self.step = step
        self.current = start - step

    def generate(self, *args, **kwargs):
        """Generate int id"""
        self.current += self.step
        return self.current

class ItemFromList(Generator):
    """Picks a random item from a choices list."""
    def __init__(self, choices=None):
        if choices and isinstance(choices, list):
            self.choices = choices
  

    def generate(self, *args, **kwargs):
        """Returns one random item from choices param"""
        return random.choice(self.choices)

class StringFromRegex(Generator):
    """Generates a random string given a regex"""
    def __init__(self, regex):
        self.regex = regex

    def generate(self, *args, **kwargs):
        return rstr.xeger(self.regex)

class IncrementalDateTime(Generator):
    """Generates increasing datetime object, the next datetime is 
       current generator datetime plus randomint(1, delta) milliseconds
    """
    def __init__(self, min_datetime='now', ms_delta_range=1000):
        self.format = '%Y-%m-%d %H:%M:%S.%f'
        self.delta = ms_delta_range
        if min_datetime == 'now':
            self.min_datetime = datetime.datetime.now()
        else:
            self.min_datetime = datetime.datetime.strptime(min_datetime, 
                                                           self.format)
        
    def generate(self, *args, **kwargs):
        ms_change = random.randint(1, self.delta)
        self.min_datetime = (self.min_datetime + 
                             datetime.timedelta(milliseconds = ms_change))
        return self.min_datetime




