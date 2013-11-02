import logging

logger = logging.getLogger('to_terminal')

class WeekdaySelectWidget(Select):
    
    """ A select widget where each option has the value 0 - 6 and the contents
    'Monday' through 'Sunday'
    """
    
    _DAYS = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Satruday'),
        (6, 'Sunday'))
    
    def __init__(self, *args, **kwargs):
        """ Constructor
        
        Optional arguments:
        
        choices: A tuple of two-tuples where each two-tuple specifies a weekday
            number and a weeekday name. The length of the tuple must be 7. This
            argument is provided in case any subclass or field wants to use a
            different format for the month (e.g. 'Mon' for 'Monday')
            
        initial_date: the date for which the month will be auto-selected. For
            instance, if the date falls on a Monday, then the widget will have
            "Monday" selected. If not given, then `date.today()` will be used.
            
        attrs: Any additional atributes for the `<select></select>` element.
        
        """
        choices = kwargs.pop('choices', self._DAYS)
        if len(choices) != 7:
            raise AssertionError('Expected choices length to be 7.' +
                                 'Recieved a lenght of %d'%(len(choices)))
        
        super(WeekdaySelectWidget, self).__init__(choices=choices, *args, **kwargs)
        
class MonthSelectWidget(Select):
    """ A widget used to select a month. Each option will contain the month
    number (0 to 11) and the month name ('January' to 'December')
    """
    _MONTHS = (
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'))
    
    def __init__(self, *args, **kwargs):
        """Constructor
        
        Optional arguments:
        
        choices: A tuple of two-tuples where each two-tuple specifies a month
            number and a month name. The length of the tuple must be 12. This
            argument is provided in case any subclass or field wants to use a
            different format for the month (e.g. 'Oct' instead of 'October')
            
        initial_date: the date for which the month will be auto-selected. For
            instance, if the date is April 3rd, 1999, then the widget will have
            "April" selected. If not given, then `date.today()` will be used.
            
        attrs: Any additional atributes for the `<select></select>` element.
        
        """
        
        choices = kwargs.pop('choices', self._MONTHS)
        
        if len(choices) != 12:
            raise ExpectedLengthException('choices', 12, len(choices))
        
        
        logger.debug('Choices: %s'%(str(choices)))
        
        super(MonthSelectWidget, self).__init__(choices=choices, 
                                                *args,
                                                **kwargs)
        
        logger.debug('Created month select widget.')
        
class DayOfMonthSelectWidget(Select):
    
    """ A widget used to select the day of the month based on a given date
    (ignoring the day, of course). Contains a select with option values from
    1 to 31, depending on the month and the year.
    """
    
    def _is_leap_year(self, year):
        return((year % 4 == 0
            and year % 100 != 0)
                or (year % 400 is 0))
    
    (JANUARY, FEBRUARY, MARCH, APRIL, MAY, JUNE, JULY, AUGUST,
     SEPTEMBER, OCTOBER, NOVEMBER, DECEMBER) = range(0, 12)
    
    _M_31 = (JANUARY, MARCH, MAY, JULY, AUGUST, OCTOBER, DECEMBER)
    _M_30 = (APRIL, JUNE, SEPTEMBER, NOVEMBER)
    
    
    def __init__(self, *args, **kwargs):
        
        """Constructor
        
        Optional Arguments:
        
        :initial_date: the date for which the day of the month will be auto-
            selected. For instance, if the date is April 3rd, 1999, then the 
            widget will have "3" selected. If not given, then `date.today()`
            will be used.
            
        :attrs: any additional attributes for the `<select></select>` element.
            
        """
        
        initial_date = kwargs.pop('initial_date', None) or date.today()
            
        max_days = 28
        if initial_date.month in self._M_31:
            max_days = 31
        elif initial_date.month in self._M_30:
            max_days = 30
        elif initial_date.month == self.FEBRUARY:
            if self._is_leap_year(initial_date.year):
                max_days = 29
            
        # construct the "choices" tuple
        choices = ()
        for i in range(1, max_days+1):
            choices += ((str(i), str(i)),)
            
        #logger.debug('choices: %s'%(str(choices)))
            
        super(DayOfMonthSelectWidget, self).__init__(choices=choices, *args, **kwargs)