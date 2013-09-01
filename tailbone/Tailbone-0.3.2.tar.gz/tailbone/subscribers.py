#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
Event Subscribers
"""

from pyramid import threadlocal

import rattail
from . import helpers


def before_render(event):
    """
    Adds goodies to the global template renderer context:

       * ``rattail``
    """

    # Import labels module so it's available if/when needed.
    import rattail.labels

    # Import SIL module so it's available if/when needed.
    import rattail.sil

    request = event.get('request') or threadlocal.get_current_request()

    renderer_globals = event
    renderer_globals['h'] = helpers
    renderer_globals['rattail'] = rattail


def includeme(config):
    config.add_subscriber('tailbone.subscribers:before_render',
                          'pyramid.events.BeforeRender')
