__all__ = ('parse', 'gettext')

import datetime

from radar.exceptions import UnrecognisedDateFormat
from radar.defaults import DATE_FORMATS

gettext = lambda s: s

def parse(timestamp, formats=None):
    """
    Parse the given datetime according to the format given.

    :param str timestamp:
    :param list formats: List of formats. Example value: ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"].
    :return datetime.datetime:
    """
    if formats is None:
        formats = DATE_FORMATS
    else:
        assert isinstance(formats, list)

    for date_format in formats:
        try:
            return datetime.datetime.strptime(timestamp, date_format)
        except:
            pass

    raise UnrecognisedDateFormat(gettext("Unrecognised date format"))
