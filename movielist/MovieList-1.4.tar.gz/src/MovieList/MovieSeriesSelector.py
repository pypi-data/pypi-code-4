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
Module: MovieList.MovieSeriesSelector
Created on: 9 Jun 2013
@author: Bob Bowles <bobjohnbowles@gmail.com>
"""

from gi.repository import Gtk
from getUnderlyingSelection import getChildModelSelection
from getUnderlyingSelection import getParentModelSelection



class MovieSeriesSelector(Gtk.HBox):
    """
    This wraps a Gtk.ComboBox with a Gtk.Label and a Gtk.Button to
    navigate and select a MovieSeries from a MovieTreeStore.
    """


    def __init__(self, parent=None, movieTreeStore=None):
        """
        Initialize the widget UI and data.
        """

        super().__init__()
        self.parent = parent
        self.movieTreeStore = movieTreeStore

        self.initializeUI()
        self.initializeModel()



    def initializeUI(self):
        """
        Create and lay out the components of the widget.
        """

        label = Gtk.Label('Parent Movie Series:')
        self.comboBox = Gtk.ComboBoxText()
        self.clearButton = Gtk.Button('Clear')

        self.pack_start(label, False, False, 0)
        self.pack_start(self.comboBox, True, True, 0)
        self.pack_start(self.clearButton, False, False, 0)
        self.show_all()

        self.clearButton.connect('clicked', self.on_clearButton_clicked)


    def initializeModel(self):
        """
        Initialize the comboBox model of the data.
        """

        comboBoxFilterModel = self.movieTreeStore.filter_new()
        comboBoxFilterModel.set_visible_func(self.comboBoxFilter, None)
        comboBoxSortModel = Gtk.TreeModelSort(model=comboBoxFilterModel)
        self.comboBoxModel = comboBoxSortModel
        self.comboBox.set_model(self.comboBoxModel)


    def comboBoxFilter(self, model, iteration, data):
        """
        Filter method to display only series entries in the comboBox views.
        """

        return model[iteration][-1]


    def getSelected(self):
        """
        Return the iteration of the selected comboBox series, or None if none is
        selected.
        """

        iteration = self.comboBox.get_active_iter()
        return getChildModelSelection(self.comboBoxModel, iteration)


    def setSelected(self, iteration):
        """
        Set the current selection of the comboBox.
        """

        # TODO: Kludge Alert:
        # the 'right' way of doing this seems to have holes in it
        # comboBoxIter = getParentModelSelection(self.comboBoxModel, iteration)
        # self.comboBox.set_active_iter(comboBoxIter)

        # TODO: This is the kludge
        if iteration:
            seriesName = self.movieTreeStore[iteration][0]
            self.comboBoxModel.foreach(self.setActiveComboBoxRow, seriesName)
        else:
            self.comboBox.set_active(-1)


    def on_clearButton_clicked(self, widget):
        """
        Callback for the clearButton.

        Clears the current selection in the comboBox.
        """

        self.comboBox.set_active(-1)


    def setActiveComboBoxRow(self, model, path, iteration, seriesName):
        """
        TODO: This is a kludge to workaround parts of the Gtk API not working.

        (see setSelected())
        """

        if model[iteration][0] == seriesName:
            self.comboBox.set_active_iter(iteration)
            return True
        return False
