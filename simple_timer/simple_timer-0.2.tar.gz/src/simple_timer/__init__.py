__title__ = 'simple_timer.__init__'
__version__ = '0.2'
__build__ = 0x000002
__author__ = 'Artur Barseghyan'

import datetime

class Timer(object):
    """
    Time class. Makes it easy to track time.

    :attribute float duration: Elapsed time in seconds in ``float`` format.
    :attribute datetime.timedelta timedelta: Elapsed time in ``datetime.timedelta`` format.
    :example:

    >>> from simple_timer import Timer
    >>> timer = Timer()
    >>> timer.stop()
    >>> print timer.timedelta
    datetime.timedelta(0, 4, 56711)
    >>> print timer.duration
    4.56711
    >>> timer.stop_and_return_timedelta()
    datetime.timedelta(0, 52, 367428)
    >>> print timer.duration
    52.367428
    >>> timer.stop_and_return_timedelta()
    datetime.timedelta(0, 167, 392662)
    >>> timer.stop_and_return_duration()
    183.344704
    >>> timer.reset()
    >>> timer.stop_and_return_timedelta()
    datetime.timedelta(0, 1, 134813)
    """
    __slots__ = ('_duration', '_timedelta', '__start_time', '__end_time')

    def __init__(self, start_time=None):
        """
        Start the timer.

        :param datetime.datetime start_time: If provided used as start time instead of ``datetime.datetime.now``
            method.
        """
        if start_time is not None:
            assert type(start_time) == datetime.datetime
            self.__start_time = start_time
        else:
            self.__start_time = datetime.datetime.now() # Task start time

        self._duration = None
        self._timedelta = None

    @property
    def duration(self):
        if not self._duration:
            td = self.timedelta
            return float("{0}.{1}".format(td.seconds, td.microseconds))
        else:
            return self._duration

    @property
    def timedelta(self):
        if not self._timedelta:
            return datetime.datetime.now() - self.__start_time
        else:
            return self._timedelta

    def stop(self, end_time=None):
        """
        Stops the timer.

        :param datetime.datetime end_time: If provided used as end time instead of ``datetime.datetime.now``
            method.

        Once the time is stopped, the ``duration`` and ``timedelta`` attributes of the timer are frozen until
        you call any of the ``stop`` methods. So, whenever you want to access the frozen data, call it
        directly.

        :example:

        >>> from simple_timer import Timer
        >>> timer = Timer()
        >>> timer.stop()
        >>> print timer.timedelta
        datetime.timedelta(0, 4, 56711)
        >>> print timer.duration
        4.56711

        Once you call any of the ``stop`` methods again, the ``duration`` and ``timedelta`` attribute of the
        timer are updated.

        :example:

        >>> timer.stop_and_return_timedelta()
        datetime.timedelta(0, 52, 367428)
        >>> print timer.duration
        52.367428
        >>> timer.stop_and_return_timedelta()
        datetime.timedelta(0, 167, 392662)
        >>> timer.stop_and_return_duration()
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
        self._duration = None
        self._timedelta = None

    def stop_and_return_duration(self, end_time=None):
        """
        Updates the values and returns the ``duration`` attribute in seconds in float format.

        :param datetime.datetime end_time: If provided used as end time instead of ``datetime.datetime.now``
            method.
        :return float: Duration in seconds in ``float`` format.
        """
        self.stop(end_time)
        return self._duration

    def stop_and_return_timedelta(self, end_time=None):
        """
        Updates the values and returns the ``timedelta`` attribute.

        :param datetime.datetime end_time: If provided used as end time instead of ``datetime.datetime.now``
            method.
        :return datetime.timedelta: Duration in ``datetime.timedelta`` format.
        """
        self.stop(end_time)
        return self._timedelta

    def __calculate(self):
        """
        Calculates and updates the ``timedelta`` and ``duration`` attributes.
        """
        self._timedelta = self.__end_time - self.__start_time
        self._duration = float("{0}.{1}".format(self._timedelta.seconds, self._timedelta.microseconds))
