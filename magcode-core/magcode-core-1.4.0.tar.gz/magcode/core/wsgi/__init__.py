#
# Copyright (c) Net24 Limited, Christchurch, New Zealand 2011-2012
#       and     Voyager Internet Ltd, New Zealand, 2012-2013
#
#    This file is part of py-magcode-core.
#
#    Py-magcode-core is free software: you can redistribute it and/or modify
#    it under the terms of the GNU  General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Py-magcode-core is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU  General Public License for more details.
#
#    You should have received a copy of the GNU  General Public License
#    along with py-magcode-core.  If not, see <http://www.gnu.org/licenses/>.
#
"""
WSGI common functions
"""

import sys
import os

from magcode.core.globals_ import *
from magcode.core.logging import setup_logging
from magcode.core.utility import *
from magcode.core.database import *


def wsgi_setup():
    """
    Setup a WSGI script.  This is here to get the weird stuff all in one place.
    """
    settings['process_type'] = PROCESS_TYPE_WSGI
    setup_logging()
    try:
        core_read_config()
        core_setup_sqlalchemy()
    except Exception as exc:
        sys.stderr.flush()
        os._exit(1)

def wsgi_outer_error(environ, start_response, status, message=None):
    if message:
        log_error("[client %s] - %s, %s" % (environ['REMOTE_ADDR'], status,
            message))
    else:
        log_error("[client %s] - %s" % (environ['REMOTE_ADDR'], status))
    start_response(status, [('Content-type', 'text/plain')])
    output = message if message else status
    return [output.encode('iso-8859-1')]

