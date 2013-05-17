import datetime

class Timer(object):
    """
    Time class. Makes it easy to track time.

    :attribute float duration: Elapsed time in seconds in `float` format.
    :attribute datetime.timedelta timedelta: Elapsed time in `datetime.timedelta` format.
    :example:

    >>> from simple_timer import Timer
    >>> my_timer = Timer()
    >>> my_timer.stop()
    >>> print my_timer.timedelta
    datetime.timedelta(0, 4, 56711)
    >>> print my_timer.duration
    4.56711
    >>> my_timer.stop_and_return_timedelta()
    datetime.timedelta(0, 52, 367428)
    >>> print my_timer.duration
    52.367428
    >>> my_timer.stop_and_return_timedelta()
    datetime.timedelta(0, 167, 392662)
    >>> my_timer.stop_and_return_duration()
    183.344704
    >>> my_timer.reset()
    >>> my_timer.stop_and_return_timedelta()
    datetime.timedelta(0, 1, 134813)
    """
    __slots__ = ('duration', 'timedelta', '__start_time', '__end_time')

    def __init__(self, start_time=None):
        """
        Start the timer.

        :param datetime.datetime start_time: If provided used as start time instead of `datetime.datetime.now()`.
        """
        if start_time is not None:
            assert type(start_time) == datetime.datetime
            self.__start_time = start_time
        else:
            self.__start_time = datetime.datetime.now() # Task start time

        self.duration = None
        self.timedelta = None

    def stop(self, end_time=None):
        """
        Stops the timer.

        :param datetime.datetime end_time: If provided used as end time instead of `datetime.datetime.now()`.

        Once the time is stopped, the `duration` and `timedelta` attributes of the timer are frozen until you call
        any of the `stop` methods. So, whenever you want to access the frozen data, call it directly.

        :example:

        >>> from simple_timer import Timer
        >>> my_timer = Timer()
        >>> my_timer.stop()
        >>> print my_timer.timedelta
        datetime.timedelta(0, 4, 56711)
        >>> print my_timer.duration
        4.56711

        Once you call any of the `stop` methods again, the `duration` and `timedelta` attribute of the timer are
        updated.

        :example:

        >>> my_timer.stop_and_return_timedelta()
        datetime.timedelta(0, 52, 367428)
        >>> print my_timer.duration
        52.367428
        >>> my_timer.stop_and_return_timedelta()
        datetime.timedelta(0, 167, 392662)
        >>> my_timer.stop_and_return_duration()
        183.344704
        """
        # Setting the `end_time`.
        if end_time is not None:
            assert type(end_time) == datetime.datetime
            self.__end_time = end_time
        else:
            self.__end_time = datetime.datetime.now() # Task end time

        assert self.__end_time > self.__start_time

        self.__calculate()

    def reset(self):
        """
        Resets all the values (kind of equal to making a new object).
        """
        self.__start_time = datetime.datetime.now()
        self.__end_time = None
        self.duration = None
        self.timedelta = None

    def stop_and_return_duration(self, end_time=None):
        """
        Updates the values and returns the `duration` attribute in seconds in float format.

        :param datetime.datetime end_time: If provided used as end time instead of `datetime.datetime.now()`.
        :return float: Duration in seconds in `float` format.
        """
        self.stop(end_time)
        return self.duration

    def stop_and_return_timedelta(self, end_time=None):
        """
        Updates the values and returns the `timedelta` attribute.

        :param datetime.datetime end_time: If provided used as end time instead of `datetime.datetime.now()`.
        :return datetime.timedelta: Duration in `datetime.timedelta` format.
        """
        self.stop(end_time)
        return self.timedelta

    def __calculate(self):
        """
        Calculates and updates the `timedelta` and `duration` attributes.
        """
        self.timedelta = self.__end_time - self.__start_time
        self.duration = float("%s.%s" % (self.timedelta.seconds, self.timedelta.microseconds))
