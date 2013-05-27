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
Module: MovieList.MovieEditDialog
Created on: 28 Mar 2013
@author: Bob Bowles <bobjohnbowles@gmail.com>
"""

from gi.repository import Gtk
from constants import MOVIE_DIALOG_BUILD_FILE as DIALOG_BUILD_FILE
from Movie import Movie
import datetime

MIN_YEAR = 1900
MIN_TIME = 0



class MovieEditDialog(object):
    """
    Dialog for adding or editing a Movie object.
    """


    def __init__(self, parent=None, movie=Movie(), seriesName=None,
                 movieTreeStore=None):
        """
        Construct and run the dialog
        """

        self.builder = Gtk.Builder()
        self.builder.add_from_file(DIALOG_BUILD_FILE)
        self.builder.connect_signals(self)

        # get a reference to the main window itself and display the window
        self.dialog = self.builder.get_object('movieEditDialog')
        self.dialog.set_transient_for(parent)

        # get the dialog editable areas
        self.titleEntry = self.builder.get_object('titleEntry')
        self.dateSpinbutton = self.builder.get_object('dateSpinbutton')
        self.directorEntry = self.builder.get_object('directorEntry')
        self.durationSpinbutton = self.builder.get_object('durationSpinbutton')
        self.starsEntry = self.builder.get_object('starsEntry')
        self.genreEntry = self.builder.get_object('genreEntry')
        self.mediaChooserButton = self.builder.get_object('mediaChooserButton')
        self.seriesComboBox = self.builder.get_object('seriesComboBox')

        # adjust the date spinbutton range for the current year
        now = datetime.datetime.now()
        self.dateSpinbutton.set_range(MIN_YEAR, now.year)

        # only list series in the seriesComboBox
        index = 0
        for row in movieTreeStore:
            if row[-1]:
                self.seriesComboBox.append(None, row[0])
                if seriesName and row[0] == seriesName:
                    self.seriesComboBox.set_active(index)
                index += 1

        # populate the dialog fields
        self.titleEntry.set_text(movie.title)
        self.dateSpinbutton.set_value(int(movie.date) if movie.date
                                      else MIN_YEAR)
        if movie.director:
            self.directorEntry.set_text(movie.director)
        self.durationSpinbutton.set_value(int(movie.duration) if movie.duration
                                          else MIN_TIME)
        if movie.stars:
            self.starsEntry.set_text(movie.stars)
        if movie.genre:
            self.genreEntry.set_text(movie.genre)
        if movie.media:
            self.mediaChooserButton.set_filename(movie.media)


    def run(self):
        """
        Display the edit dialog and return any changes.
        """

        # self.dialog.show()
        response = self.dialog.run()
        movie = None
        seriesName = None

        # if the ok button was pressed update the movie object
        if response == Gtk.ResponseType.OK:

            # deal with default minimums
            date = self.dateSpinbutton.get_value_as_int()
            if date == MIN_YEAR:
                date = ''
            duration = self.durationSpinbutton.get_value_as_int()
            if duration == MIN_TIME:
                duration = ''

            movie = Movie(title=self.titleEntry.get_text(),
                          date=date,
                          director=self.directorEntry.get_text(),
                          duration=duration,
                          stars=self.starsEntry.get_text(),
                          genre=self.genreEntry.get_text(),
                          media=self.mediaChooserButton.get_filename(),
                          # series=self.seriesComboBox.get_active_text()
                          )
            seriesName = self.seriesComboBox.get_active_text()

        else:
            movie = Movie()

        self.dialog.destroy()
        return response, movie, seriesName


    def on_seriesClearButton_clicked(self, widget):
        """
        Reset the series name to None.
        """

        self.seriesComboBox.set_active(-1)



if __name__ == '__main__':

    app = MovieEditDialog()
    response, movie = app.run()
    print(movie)
