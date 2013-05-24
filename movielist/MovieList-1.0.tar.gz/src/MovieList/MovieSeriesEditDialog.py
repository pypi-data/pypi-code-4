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
Module: MovieList.MovieSeriesEditDialog
Created on: 25 Apr 2013
@author: Bob Bowles <bobjohnbowles@gmail.com>
"""

from gi.repository import Gtk
from constants import SERIES_DIALOG_BUILD_FILE as DIALOG_BUILD_FILE
from Movie import MovieSeries



class MovieSeriesEditDialog(object):
    """
    Dialog for adding or editing a MovieSeries object.
    """


    def __init__(self, parent=None, series=MovieSeries()):
        """
        Construct and run the dialog
        """

        self.builder = Gtk.Builder()
        self.builder.add_from_file(DIALOG_BUILD_FILE)
        self.builder.connect_signals(self)

        # get a reference to the main window itself and display the window
        self.dialog = self.builder.get_object('movieSeriesEditDialog')
        self.dialog.set_transient_for(parent)

        # get the dialog editable areas
        self.titleEntry = self.builder.get_object('titleEntry')

        # populate the dialog fields
        self.titleEntry.set_text(series.title)

        # retain the list of child movies
        self.seriesChildren = series.series


    def run(self):
        """
        Display the edit dialog and return any changes.
        """

        # self.dialog.show()
        response = self.dialog.run()
        series = None

        # if the ok button was pressed update the movie object
        if response == Gtk.ResponseType.OK:
            series = MovieSeries(title=self.titleEntry.get_text())
            series.series = self.seriesChildren
        else:
            series = MovieSeries()

        self.dialog.destroy()
        return response, series



if __name__ == '__main__':
    window = Gtk.Window()
    app = MovieSeriesEditDialog(parent=window)
    response, series = app.run()
    print(series)
