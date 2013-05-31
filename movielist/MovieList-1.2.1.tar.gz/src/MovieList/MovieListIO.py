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
from fileinput import filename

"""
Module: MovieList.MovieListIO
Created on: 1 Apr 2013
@author: Bob Bowles <bobjohnbowles@gmail.com>
"""

import io
import pickle
from lxml import etree
from Movie import Movie, MovieSeries

SAVE, LOAD = 0, 1



class MovieListIO(object):
    """
    This module is responsible for saving and loading movie data in the
    MovieList to disk.
    At time of initial writing this may not need to be very complicated.
    However, it is expected that later more than one data format will be
    supported, and it seemed wise to delegate all i/o to a dedicated module to
    avoid cluttering up the main application.
    """


    def __init__(self, movieList=None):
        """
        Initialize the reference to the parent so we can access the necessary
        data.
        """

        self.ioMethods = {
                  'pickle': [self.savePickle, self.loadPickle],
                  'xml': [self.saveXml, self.loadXml]
                  }

        self.movieList = movieList


    def getFileExtension(self):
        """
        Work out what kind of file we are using.
        """

        return self.movieList.getFileName().split('.')[-1]


    def save(self):
        """
        Save the data.

        We select the appropriate save method using the filename extension as a
        key to the io methods dictionary.
        """

        # extract the data from the movieListStore
        treeIter = self.movieList.movieTreeStore.get_iter_first()
        outputList = self.extractMovieTreeAsList(treeIter)
        self.ioMethods[self.getFileExtension()][SAVE](outputList)


    def savePickle(self, outputList):
        """
        Save the data to disk as a pickle.
        """

        # pickle the data
        fileHandler = io.open(self.movieList.getFileName(), 'wb')
        pickle.dump(outputList, fileHandler)
        fileHandler.close()


    def saveXml(self, outputList):
        """
        Save the data in the form of an xml document.

        Iterate over the gtk treeView to create an lxml etree document, then
        write the document to the specified file.
        """

        # extract the data from the list into an etree document
        root = etree.Element('root')

        for object in outputList:
            if isinstance(object, MovieSeries):
                self.addSeriesToXml(root, object)
            else:
                self.addMovieToXml(root, object)

        # save the tree structure in an xml file
        tree = etree.ElementTree(root)
        tree.write(self.movieList.getFileName(),
                   pretty_print=True,
                   encoding='ISO-8859-1',
                   xml_declaration=True)


    def addMovieToXml(self, node, movie):
        """
        Add a movie object to the xml tree at the element node specified.
        """

        movieNode = etree.SubElement(node, 'movie')

        self.addSingleNodeToXml(movieNode, movie.title, 'title')
        self.addSingleNodeToXml(movieNode, movie.date, 'date')
        self.addMultipleNodesToXml(movieNode, movie.director, 'director')
        self.addSingleNodeToXml(movieNode, movie.duration, 'duration')
        self.addMultipleNodesToXml(movieNode, movie.stars, 'star')
        self.addMultipleNodesToXml(movieNode, movie.genre, 'genre')
        self.addSingleNodeToXml(movieNode, movie.media, 'media')


    def addSeriesToXml(self, node, series):
        """
        Add a series object, its data and its child movies to the xml tree at
        the specified node.
        """

        seriesNode = etree.SubElement(node, 'series')

        self.addSingleNodeToXml(seriesNode, series.title, 'title')
        for movie in series.series:
            self.addMovieToXml(seriesNode, movie)


    def addSingleNodeToXml(self, node, data, tag):
        """
        Construct a sub-element of the node to contain the data.
        """

        dataNode = etree.SubElement(node, tag)
        dataNode.text = data


    def addMultipleNodesToXml(self, node, semiColonDataText, tag):
        """
        Construct child nodes to hold the text data from a semicolon-delimited
        string.
        """

        if semiColonDataText:
            dataList = semiColonDataText.split(';')
            for data in dataList:
                self.addSingleNodeToXml(node, data.strip(), tag)


    def extractMovieTreeAsList(self, treeIter):
        """
        Extract the movie data from the movieTreeStore in the form of a list.

        Recursively construct a list of the movies and series in the rows and
        child rows of the store.
        The base treeIter should point to the tree root, i.e.,
        movieTreeStore.get_iter_first().
        The list is sorted by title before returning.
        """

        list = []
        while treeIter:
            if self.movieList.movieTreeStore.iter_has_child(treeIter):
                seriesList = []
                childIter = \
                    self.movieList.movieTreeStore.iter_children(treeIter)
                seriesList.extend(self.extractMovieTreeAsList(childIter))
                list.append(
    MovieSeries.fromList(self.movieList.movieTreeStore[treeIter], seriesList))
            else:
                list.append(
    Movie.fromList(self.movieList.movieTreeStore[treeIter]))

            treeIter = self.movieList.movieTreeStore.iter_next(treeIter)

        return sorted(list, key=lambda item:item.title)


    def load(self):
        """
        Load the data.

        We select and invoke the appropriate method using the file extension as
        a key to the io methods dictionary.
        The list of movie objects is then inserted into the gtk movieTreeStore.
        """

        inputList = self\
        .ioMethods[self.getFileExtension()][LOAD](self.movieList.getFileName())

        # load the data into the movieListStore
        self.movieList.movieTreeStore.clear()
        self.populateMovieTreeStore(inputList)


    def loadPickle(self, fileName):
        """
        Return the data from a pickle file as a list. It is assumed the
        unpickled objects are Movies or MovieSeries.
        """

        try:
            fileHandler = io.open(fileName, 'rb')
            return pickle.load(fileHandler)
        finally:
            fileHandler.close()


    def loadXml(self, filename):
        """
        Load the data from an xml file.

        Use lxml to parse the data, return it as a list of movie objects.
        """

        # read the xml file into an lxml etree document
        doc = etree.parse(filename)

        # get the data out of the etree into a list of objects
        root = doc.getroot()
        inputList = []
        for element in root.getchildren():
            if element.tag == 'movie':
                inputList.append(self.getMovieFromXml(element))
            elif element.tag == 'series':
                inputList.append(self.getSeriesFromXml(element))
            else:
                print('Unknown tag: {}'.format(element.tag))
        return inputList


    def getSeriesFromXml(self, series):
        """
        Obtain a movie series from an xml tree object as a list of movies.
        """

        seriesTitle = series.findtext('title')

        # get the movies in the series
        seriesList = []
        movieNodes = series.findall('movie')
        for movie in movieNodes:
            seriesList.append(self.getMovieFromXml(movie))

        return MovieSeries(title=seriesTitle, series=seriesList)


    def getMovieFromXml(self, movieElement):
        """
        Extract xml data as a Movie object.
        """

        title = movieElement.findtext('title')
        date = movieElement.findtext('date')
        director = self.getDataFromMultipleNodes(movieElement, 'director')
        duration = movieElement.findtext('duration')
        stars = self.getDataFromMultipleNodes(movieElement, 'star')
        genre = self.getDataFromMultipleNodes(movieElement, 'genre')
        media = movieElement.findtext('media')

        return Movie(title=title,
                     date=date,
                     director=director,
                     duration=duration,
                     stars=stars,
                     genre=genre,
                     media=media,
                     )


    def getDataFromMultipleNodes(self, node, tag):
        """
        Extract the text data from a particular tagged child node type as a
        comma-separated list.
        """

        dataList = []
        children = node.findall(tag)
        for child in children:
            if child.text:
                dataList.append(child.text)

        if dataList and dataList[0]:
            return ', '.join(dataList)
        else:
            return None


    def populateMovieTreeStore(self, movieList):
        """
        Populate the treeStore from a list of movies and movie series.
        """

        for movie in movieList:
            if isinstance(movie, MovieSeries):
                self.appendSeriesToStore(movie)
            else:
                self.appendMovieToStore(movie, None)


    def appendSeriesToStore(self, series):
        """
        Append a movie series to the movieTreeStore.

        Append the series, then append its movies as its children.
        """

        seriesIter = self.movieList.movieTreeStore.append(None, series.toList())
        for movie in series.series:
            self.appendMovieToStore(movie, seriesIter)


    def appendMovieToStore(self, movie, seriesIter):
        """
        Append a movie to the treeStore.

        The movie is appended as a child of the series indicated by
        the iterator. If the iterator is null the movie is appended to the root.
        """

        self.movieList.movieTreeStore.append(seriesIter, movie.toList())


    def importCsv(self):
        """
        Import CSV data.

        The assumed format for the csv data lines is as follows:
        title,date,director,duration,genre,stars,other_stuff_can_be_ignored

        The assumed format of lists such as directors, stars, and genres is
        semicolon-separated (';'). These are converted to comma-separated
        values before adding to the tree.

        NOTE: No attempt is made to preserve information about media or series.
        """

        fileHandler = io.open(self.movieList.getFileName(), 'rt')

        # get the data and add it to the list store.
        self.movieList.movieTreeStore.clear()
        while True:
            data = fileHandler.readline()
            if not data:
                break
            dataList = data[:-1].split(',')
            movie = Movie(
                          title=dataList[0],
                          date=(int(dataList[1]) if dataList[1].isnumeric()
                                else 1900),
                          director=dataList[2].replace(';', ','),
                          duration=(int(dataList[3]) if dataList[3].isnumeric()
                                    else 0),
                          genre=dataList[4].replace(';', ','),
                          stars=dataList[5].replace(';', ','),
                          )
            self.movieList.movieTreeStore.append(None, movie.toList())
        fileHandler.close()
