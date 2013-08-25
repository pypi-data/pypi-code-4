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
Module: MovieList.Movie
Created on: 28 Mar 2013
@author: Bob Bowles <bobjohnbowles@gmail.com>
"""


# constants to define sensible default values
DEFAULT_DATE = ''
DEFAULT_DURATION = ''
DEFAULT_TEXT = ''


class Movie(object):
    """
    A data wrapper for managing movie data.
    """


    def __init__(self,
                 title=DEFAULT_TEXT,
                 date=DEFAULT_DATE,
                 director=DEFAULT_TEXT,
                 duration=DEFAULT_DURATION,
                 stars=DEFAULT_TEXT,
                 genre=DEFAULT_TEXT,
                 media=DEFAULT_TEXT,
                 ):
        """
        Initialize a movie's data attributes.

        Some care is needed converting nulls between ints and strings for the
        'numeric' fields date and duration.
        """

        self.title = title
        self.date = '{0:>4s}'.format(str(date)) if date else ''
        self.director = director
        self.duration = '{0:>3s}'.format(str(duration)) if duration else ''
        self.stars = stars
        self.genre = genre
        self.media = media


    def toList(self):
        """
        Publish the movie data as a list.

        The order of parameters in the list is:
        0    title        the name of the movie
        1    date         the year of publication (if known)
        2    director     the director(s) (comma-delimited text)
        3    duration     the time the movie runs for (mins)
        4    stars        the main stars cited (comma-delimited text)
        5    genre        the movie's genre (comma-delimited text)
        6    media        the location of the movie file on the local system
        7    False        only used in the treeStore
        """

        # fix for legacy versions with numeric attributes
        date = '{0:>4s}'.format(str(self.date)) if self.date else ''
        duration = '{0:>3s}'.format(str(self.duration)) if self.duration else ''

        return [self.title,
                date,
                self.director,
                duration,
                self.stars,
                self.genre,
                self.media,
                False,  # identifies this list as a movie not a series
                ]


    @staticmethod
    def fromList(listObject):
        """
        Convert a list-like object into a Movie.

        This reverses the effect of self.toList(), and assumes the same order of
        parameters in the list.
        """

        return Movie(title=listObject[0],
                     date=listObject[1],
                     director=listObject[2],
                     duration=listObject[3],
                     stars=listObject[4],
                     genre=listObject[5],
                     media=listObject[6],
                     )


    def __repr__(self):

        return ("Movie(title='{0.title}', "
                "date={0.date}, "
                "director='{0.director}', "
                "duration={0.duration}, "
                "stars='{0.stars}', "
                "genre='{0.genre}', "
                "media='{0.media}', "
                ).format(self)


    def __eq__(self, other):

        return self.__dict__ == other.__dict__

    def __gt__(self, other):

        if self.title > other.title:
            return True
        elif self.title == other.title:
            if isinstance(other, MovieSeries):
                return True
            else:
                return self.date > other.date
        return False

    def __lt__(self, other):

        if self.title < other.title:
            return True
        elif self.title == other.title:
            if isinstance(other, MovieSeries):
                return False
            else:
                return self.date < other.date
        return False


class MovieSeries(Movie):
    """
    A subclass of Movie that is intended to act as a container for a movie
    series.

    Unlike Movie, the only important attributes are the series title, and the
    list of movies in the series.
    """


    def __init__(self, title=DEFAULT_TEXT, series=[]):
        """
        Initialize the attributes.
        """

        self.title = title
        self.series = series


    def toList(self):
        """
        Publish the series data as a list.

        The order of parameters in the list is:
        0    title        the name of the movie
        1-6  None         not applicable to a series
        7    True         only used in the treeStore
        """

        return [self.title,
                None, None, None, None, None, None,
                True,  # identifies this list as a series not a movie
                ]


    @staticmethod
    def fromList(listObject, listOfMovies):
        """
        Converts a list-like object (eg., from a movieTreeStore row) and a list
        of movies into a MovieSeries.

        The series title is the first component in the list. The movies in the
        list are the movies in the series.
        """

        return MovieSeries(title=listObject[0], series=listOfMovies)


    def __repr__(self):

        series = None
        if self.series:
            series = "'{}'".format(self.series)
        return ("MovieSeries(title='{0.title}', "
                "series={0.series}, "
                ")"
               ).format(self)



if __name__ == '__main__':

    import doctest
    doctest.testmod()
