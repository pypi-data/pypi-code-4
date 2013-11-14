"""
This package contains notification implementations.

A notification class should be implemented in the following way:
 - The constructor accepts a config dictionary.
 - Implements :meth:`notify()`. It should take a list of posts and do
   what it is supposed to do, such as sending emails to users. It must handle all
   exceptions expected in normal use and raise only instances of
   :class:`~webalerts.exceptions.NotificationException` or
   :class:`~webalerts.exceptions.ConfigurationError` if necessary.

"""
