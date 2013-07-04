"""
Override the following values in your global ``settings`` module by adding `ADMIN_TIMELINE_` prefix to the values.
When it comes to importing the values, import them from ``admin_timeline.settings`` module (without the
`ADMIN_TIMELINE_` prefix).

``NUMBER_OF_ENTRIES_PER_PAGE``: Number of entries per page.
``SINGLE_LOG_ENTRY_DATE_FORMAT``: Date format for the single log entry. Default value is "g:i:s A".
``LOG_ENTRIES_DAY_HEADINGS_DATE_FORMAT``: Day headings date format. Default value is "l j F Y".
``ENABLE_CONTENT_TYPE_FILTER``: If set to True, filtering by content type is enabled. Default value True.
``ENABLE_USER_FILTER``: If set to True, filtering by user is enabled. Default value True.
"""

__title__ = 'admin_timeline.settings'
__version__ = '0.7'
__build__ = 0x000007
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__all__ = ('NUMBER_OF_ENTRIES_PER_PAGE', 'SINGLE_LOG_ENTRY_DATE_FORMAT', 'LOG_ENTRIES_DAY_HEADINGS_DATE_FORMAT')

from admin_timeline.conf import get_setting

NUMBER_OF_ENTRIES_PER_PAGE = get_setting('NUMBER_OF_ENTRIES_PER_PAGE')
SINGLE_LOG_ENTRY_DATE_FORMAT = get_setting('SINGLE_LOG_ENTRY_DATE_FORMAT')
LOG_ENTRIES_DAY_HEADINGS_DATE_FORMAT = get_setting('LOG_ENTRIES_DAY_HEADINGS_DATE_FORMAT')
ENABLE_CONTENT_TYPE_FILTER = get_setting('ENABLE_CONTENT_TYPE_FILTER')
ENABLE_USER_FILTER = get_setting('ENABLE_USER_FILTER')

DEBUG = get_setting('DEBUG')
