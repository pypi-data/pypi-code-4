# Copyright (C) 2013 Bob Bowles <bobjohnbowles@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Module: MovieList.TreeModelHelper
Created on: 8 Jun 2013
@author: Bob Bowles <bobjohnbowles@gmail.com>
"""

from gi.repository import Gtk


def getChildModelSelection(parentModel, iteration):
    """
    Drill down into the child models of the view to find the base model and
    iteration of the current selection.
    """

    if not iteration:
        return None

    childModel = parentModel.get_model()
    childIter = parentModel.convert_iter_to_child_iter(iteration)

    if isinstance(childModel, Gtk.TreeStore):
        return childIter
    else:
        return getChildModelSelection(childModel, childIter)


def getParentModelSelection(parentModel, iteration, recursion=0):
    """
    TODO: KLUDGE ALERT: This does not seem to work. Returns a StructMeta
    instead of a Gtk.TreeIter. Note all the diagnostics.

    Find the highest-level ancestor iteration of the model from the child
    iteration given.
    """

    print('Recursion level={}'.format(recursion))
    if not iteration:
        print('No iteration, so None')
        return None

    if isinstance(parentModel, Gtk.TreeStore):
        print('TreeStore, returning iteration unaltered')
        print('Leaving bottom recursion {}'.format(recursion))
        return iteration

    else:
        childModel = parentModel.get_model()
        print('Recursing the next child...')
        childIter = getParentModelSelection(childModel, iteration, recursion + 1)
        print('Converting child iter to parent iter')
        parentIter = parentModel.convert_child_iter_to_iter(childIter)
        print('Leaving recursion {}'.format(recursion))
        return parentIter
