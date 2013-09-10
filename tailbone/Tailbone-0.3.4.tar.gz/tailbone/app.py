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
Application Entry Point
"""

from pyramid.config import Configurator

import os.path
import edbob

from sqlalchemy import engine_from_config
from .db import Session
from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.authentication import SessionAuthenticationPolicy
from .auth import TailboneAuthorizationPolicy


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """

    # Use Tailbone templates by default.
    settings.setdefault('mako.directories', ['tailbone:templates'])

    # Make two attempts when "retryable" errors happen during transactions.
    # This is intended to gracefully handle database restarts.
    settings.setdefault('tm.attempts', 2)

    config = Configurator(settings=settings)

    # Initialize edbob, dammit.
    edbob.init('rattail', os.path.abspath(settings['edbob.config']))
    edbob.init_modules(['edbob.time'])

    # Configure the primary database session.
    engine = engine_from_config(settings)
    Session.configure(bind=engine)
    Session.configure(extension=ZopeTransactionExtension())

    # Configure user authentication / authorization.
    config.set_authentication_policy(SessionAuthenticationPolicy())
    config.set_authorization_policy(TailboneAuthorizationPolicy())

    # Bring in some Pyramid goodies.
    config.include('pyramid_beaker')
    config.include('pyramid_tm')

    # Bring in the rest of Tailbone.
    config.include('tailbone')

    # Consider PostgreSQL server restart errors to be "retryable."
    config.add_tween('edbob.pyramid.tweens.sqlerror_tween_factory',
                     under='pyramid_tm.tm_tween_factory')

    return config.make_wsgi_app()
