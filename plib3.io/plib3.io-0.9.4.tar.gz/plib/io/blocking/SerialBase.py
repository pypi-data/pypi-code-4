#!/usr/bin/env python3
"""
Module SerialBase
Sub-Package IO.BLOCKING of Package PLIB3
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the blocking I/O SerialBase class.
"""

from plib.io.serial import SerialData, SerialIOBase


class SerialBase(SerialData, SerialIOBase):
    """Base class for blocking serial I/O with data handling.
    """
    
    blocking_mode = True
