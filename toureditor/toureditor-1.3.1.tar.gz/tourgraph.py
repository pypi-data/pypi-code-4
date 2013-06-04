#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-
# ----------------------------------------
# Copyright (C) 2010-2011  Frank Pählke
#
# This file is part of TourEditor.
#
# TourEditor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TourEditor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TourEditor.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------

import sys
from toureditorlib.tourfile import TourFile
from toureditorlib.tourgraph_matplotlib import TourFileFigure

encoding = 'iso-8859-1'
infilename = sys.argv[1]
outfilename = sys.argv[2]

sys.stdout.write ('Converting %s to %s\n' % (infilename, outfilename))

tourfile = TourFile.read (infilename, encoding)
fig = TourFileFigure (tourfile)
fig.save(outfilename)
