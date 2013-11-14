"""
This package contains site-specific implementations on how to interact with
the site.

A site class should be implemented in the following way:
 - The constructor accepts a config dictionary. Typical configuration values
   include ``username`` and ``password`` for sites that require authentication.
 - Implements :meth:`get_new_posts()`. It should return a list of
   :class:`~webalerts.Post` objects since the last time it is called sorted by
   published time in ascending order, or an empty list if it is the first call.
   It must handle exceptions expected in normal use and raise only
   instances of :class:`~webalerts.exceptions.SiteException` or
   :class:`~webalerts.exceptions.ConfigurationError` if necessary.

"""
