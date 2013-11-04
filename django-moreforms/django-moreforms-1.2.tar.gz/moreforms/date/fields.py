from django.forms.fields import Field, ChoiceField
from widgets import *
import logging
from datetime import date

logger = logging.getLogger('to_terminal')

""""
TEMPLATE

class ###(ChoiceField):
    
    def __init__(self, *args, **kwargs):
        
        super(###, self).__init__(widget=###, *args, **kwargs)
"""

class WeekdaySelect(Field):
    
    """ A field to select the day of the week (e.g. "Monday")
    
    # Optional arguments: #
    
    :initial_date: The initial date. When th field is rendered the weekday of
    this date will be automatically selected. Default will be `date.today()`
    
    """
    
    def __init__(self, initial_date=None, *args, **kwargs):
        
        super(WeekdaySelect, self).__init__(
            widget=WeekdaySelectWidget(),
            *args, **kwargs)
        
class MonthSelect(Field):
    
    """ A field to select the month (e.g. "January")
    
    # Optional arguments: #
    
    :initial_date: The initial date. When th field is rendered the month of
    this date will be automatically selected. Default will be `date.today()`
    
    """
    
    def __init__(self, initial_date=None, *args, **kwargs):
        super(MonthSelect, self).__init__(
            widget=MonthSelectWidget(),
            *args, **kwargs)
        
class DayOfMonthSelect(Field):
    
    """ A field to select the day of the week (e.g. "Monday")
    
    # Optional arguments: #
    
    :param initial_date: The initial date. When th field is rendered the day of
    the month for this date will be automatically selected. Default will be 
    `date.today()`
    
    """
    
    def __init__(self, *args, **kwargs):
        
        initial_date = kwargs.pop('initial_date', None)
        
        super(DayOfMonthSelect, self).__init__(
            widget=DayOfMonthSelectWidget(),
            *args, **kwargs)
        
class YearSelect(ChoiceField):
    
    def __init__(self, *args, **kwargs):
        
        start=kwargs.pop('min_year', date.today().year-200)
        end=kwargs.pop('max_year', date.today().year)
        
        choices = ()
        r = range(start, end+1)
        r.reverse()
        for i in r:
            choices = choices + ((i, i),)
            
        super(YearSelect, self).__init__(choices=choices)