# -*- coding: utf-8 -*-

# fch_util.py --- Utility functions for flo-check-homework
# Copyright (c) 2011, 2012, 2013 Florent Rougon
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA  02110-1301 USA.

import logging

def setup_logging(level=logging.NOTSET, chLevel=None):
    global logger

    if chLevel is None:
        chLevel = level

    logger = logging.getLogger('flo_check_homework.fch_util')
    logger.setLevel(level)
    # Create console handler and set its level
    ch = logging.StreamHandler() # Uses sys.stderr by default
    ch.setLevel(chLevel)  # NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
    # Logger name with :%(name)s... many other things available
    formatter = logging.Formatter("%(levelname)s %(message)s")
    # Add formatter to ch
    ch.setFormatter(formatter)
    # Add ch to logger
    logger.addHandler(ch)

setup_logging()


def loadOrInitSetting(qsettings, key, default=None, globals_dict=None,
                      locals_dict=None):
    """Load a value from a QSettings. If undefined, store the default value.

    If the setting is undefined, the default value is stored into the
    QSettings and returned.

    Use strings obtained from Python repr() to represent arbitrary
    Python objects.

    """
    if locals_dict is None:
        locals_dict = {}
    if globals_dict is None:
        globals_dict = {}

    # This has changed a lot between PyQt 4.7.3 and PyQt 4.9.6
    s = qsettings.value(key, None)
    # logger.debug("loadOrInitSetting: s = {!r}".format(s))
    if s is None:
        qsettings.setValue(key, repr(default))
        return default
    else:
        return eval(s, globals_dict, locals_dict)


def loadOrInitIntSetting(qsettings, key, default=0):
    """Load an integer value from a QSettings.

    If the setting is undefined, the default value is stored into the
    QSettings and returned. If the setting in QSettings can't be
    converted to an integer, it is replaced by the default value.

    Contrary to loadOrInitSetting, values used here must be integers. They
    are stored as is into the QSettings, without resorting to Python
    repr() before calling qsettings.setValue().

    """
    if not qsettings.contains(key):
        qsettings.setValue(key, default)

    # This has changed a lot between PyQt 4.7.3 and PyQt 4.9.6
    try:
        val = int(qsettings.value(key))
    except ValueError:
        qsettings.setValue(key, default)
        val = default

    return val
