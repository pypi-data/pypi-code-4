#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# @date: Wed May 8 19:18:16 CEST 2013
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
The MNIST Database is a database of handwritten digits, which has a training 
set of 60,000 examples, and a test set of 10,000 examples. It is a subset of
a larger set available from NIST. The digits have been size-normalized and
centered in a fixed-size image. You can download the MNIST database from:
http://yann.lecun.com/exdb/mnist/
"""

from .query import Database

__all__ = dir()

