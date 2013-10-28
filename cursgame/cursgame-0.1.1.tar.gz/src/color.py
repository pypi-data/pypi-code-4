# Copyright 2013 Sven Bartscher
# Licensed under the EUPL, Version 1.1 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
#
# http://ec.europa.eu/idabc/eupl
#
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.

# This file is part of cursgame 0.1.1

"""This module contains functions and constants related to colors.
Most of them are only wrappers to the underlying curses functions/constants."""

from curses import (COLOR_BLACK as BLACK_RAW,
                    COLOR_BLUE as BLUE_RAW,
                    COLOR_CYAN as CYAN_RAW,
                    COLOR_GREEN as GREEN_RAW,
                    COLOR_MAGENTA as MAGENTA_RAW,
                    COLOR_RED as RED_RAW,
                    COLOR_WHITE as WHITE_RAW,
                    COLOR_YELLOW as YELLOW_RAW,
                    init_pair, #For manually defining color pairs.
                    color_pair) #And finally get them.
from itertools import count

def make_colorcons(value):
    """This function makes a function containing the colorconstant.
    It is needed to seperate the namespaces of the constants."""
    def colorcons():
        return color_pair(value)
    return colorcons

d = globals()
for symbol, value in zip(('WHITE',
                          'RED',
                          'GREEN',
                          'YELLOW',
                          'BLUE',
                          'MAGENTA',
                          'CYAN',
                          'BLACK'),
                         range(8)):
    colorcons = make_colorcons(value)
    d[symbol] = colorcons
del d
