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
Module: MovieList.MovieList
Created on: 24 Mar 2013
@author: Bob Bowles <bobjohnbowles@gmail.com>
"""

import os, subprocess
from gi.repository import Gtk, Gdk
from configparser import SafeConfigParser
from constants import UI_BUILD_FILE, VERSION
from constants import CONFIG_FILE
from constants import FILE_SECTION, CURRENT_FILE
from constants import UI_SECTION, WINDOW_SIZE, COLUMN_WIDTHS
from constants import MEDIA_SECTION, MEDIA_DIR
from Movie import Movie, MovieSeries
from MovieEditDialog import MovieEditDialog
from MovieSeriesEditDialog import MovieSeriesEditDialog
from MovieListIO import MovieListIO
from getUnderlyingSelection import getChildModelSelection


# 'constants' for statusbar io
ADD = 'add'
COPY = 'copy'
EDIT = 'edit'
DELETE = 'delete'
PLAY = 'play'
OK = 0
ABORT = 1
WARN = 2
DATE = '({})'
CONTEXT = {ADD: ['Added: {} {}', 'Add aborted', ''],
           COPY: ['Copied: {} {}', 'Copy aborted',
                  'Copy: Select a movie to copy'],
           EDIT: ['Edited: {} {}', 'Edit aborted',
                  'Edit: Select a movie to edit'],
           DELETE: ['Deleted: {} {}', 'Delete aborted',
                    'Delete: Select a movie to delete'],
           PLAY: ['Played: {}', 'Play aborted',
                  'Play: no media to play']
           }
MOVIE_RESPONSE = 1
MOVIE_SERIES_RESPONSE = 2


def modifyMovieTreeStore(method):
    """
    Decorator for methods to modify a movieTreeStore.
    """

    def wrapper(self, contextId, context, response,
                 treeIndex,
                 originalMovieEntity, originalSeriesIndex,
                 modifiedMovieEntity, modifiedSeriesIndex):

        # check for a positive user dialog response and the entity has changed
        if (response == Gtk.ResponseType.OK and
            ((modifiedMovieEntity != originalMovieEntity
              if modifiedMovieEntity and originalMovieEntity else True) or
             (modifiedSeriesIndex != originalSeriesIndex
              if modifiedSeriesIndex and originalSeriesIndex else True))):

            # apply the modifications
            method(self, treeIndex,
                   originalMovieEntity, originalSeriesIndex,
                   modifiedMovieEntity, modifiedSeriesIndex)

            # write to status bar
            date = ''
            if not isinstance(originalMovieEntity, MovieSeries):
                date = (DATE.format(modifiedMovieEntity.date)
                        if modifiedMovieEntity
                        else DATE.format(originalMovieEntity.date))
            title = (modifiedMovieEntity.title
                           if modifiedMovieEntity else
                           originalMovieEntity.title)
            self.statusbar.push(contextId,
                                CONTEXT[context][OK].format(title, date))

            self.setDirty(True)

        else:
            self.statusbar.push(contextId, CONTEXT[context][ABORT])

    return wrapper



class MovieList:
    """
    The MovieList object
    """


    def __init__(self):
        """
        Initialise the MovieList.

        Initialise the UI, apply custom settings not dealt with in Glade,
        restore configuration settings.
        """

        # load the UI elements
        self.initializeUI()

        # apply custom settings not provided in the glade file
        self.customiseRendering()
        self.customiseFilter()

        # get saved configuration settings and restore them
        self.restoreConfiguration()

        # add the io module, load in the data
        self.movieListIO = MovieListIO(self)
        if self.__filename:
            self.movieListIO.load()

        # get a reference to the main window itself and display the window
        self.window.show_all()


    # other action(s) go here

    def initializeUI(self):
        """
        Initialize the UI window and its components.

        Start the UI and get references to widgets we will need to refer to
        later.
        """

        self.builder = Gtk.Builder()
        self.builder.add_from_file(UI_BUILD_FILE)
        self.builder.connect_signals(self)

        # references to the widgets we need to manipulate
        self.movieTreeStore = self.builder.get_object('movieTreeStore')
        self.movieTreeView = self.builder.get_object('movieTreeView')
        self.movieTreeViewColumns = self.movieTreeView.get_columns()
        self.movieTreeSelection = self.builder.get_object('movieTreeSelection')
        self.movieTreeModelFilter = \
            self.builder.get_object('movieTreeModelFilter')
        self.filterMovieEntry = self.builder.get_object('filterMovieEntry')
        self.statusbar = self.builder.get_object('statusbar')
        self.fileSaveAction = self.builder.get_object('fileSaveAction')
        self.window = self.builder.get_object('window')


    def restoreConfiguration(self):
        """
        Get the last configuration of the Movie List and restore the values.
        """

        self.configuration = SafeConfigParser()
        configList = self.configuration.read([CONFIG_FILE], encoding='utf-8')
        if configList:

            # restore the last open file
            if os.path.exists(self.configuration[FILE_SECTION][CURRENT_FILE]):
                self.__filename = self.configuration[FILE_SECTION][CURRENT_FILE]
                self.window.set_title(os.path.basename(self.__filename))
            else:
                self.__filename = None

            # restore the last saved window size
            if self.configuration[UI_SECTION][WINDOW_SIZE]:
                geometry = \
                    self.configuration[UI_SECTION][WINDOW_SIZE].split(',')
                x, y = (int(coord) for coord in geometry)
                self.window.resize(x, y)

            # restore the last saved column widths
            if self.configuration[UI_SECTION][COLUMN_WIDTHS]:
                columnWidths = eval(self.configuration[UI_SECTION]
                                    [COLUMN_WIDTHS])
                columns = self.movieTreeView.get_columns()
                for i in range(len(columns)):
                    columns[i].set_min_width(columnWidths[i])
                    columns[i].connect('notify::width',
                                       self.on_column_width_changed)

            # restore the last used media directory
            if os.path.exists(self.configuration[MEDIA_SECTION][MEDIA_DIR]):
                self.__mediaDir = self.configuration[MEDIA_SECTION][MEDIA_DIR]
            else:
                self.__mediaDir = None

        else:  # first time, create a vanilla configuration
            self.__filename = None
            self.__mediaDir = None
            self.configuration.add_section(FILE_SECTION)
            self.configuration.add_section(UI_SECTION)
            self.configuration.add_section(MEDIA_SECTION)
            self.saveConfiguration()

        # make sure the dirty flag is initialised
        self.__dirty = True
        self.setDirty(False)


    def saveConfiguration(self):
        """
        Save any changes to the configuration options.
        """

        self.configuration.set(FILE_SECTION, CURRENT_FILE,
                               self.__filename if self.__filename else '')
        self.configuration.set(UI_SECTION, WINDOW_SIZE,
                               ', '.join(str(coord)
                                         for coord in self.window.get_size()))

        columnWidths = []
        columns = self.movieTreeView.get_columns()
        for column in columns:
            columnWidths.append(column.get_width())
        self.configuration.set(UI_SECTION, COLUMN_WIDTHS, repr(columnWidths))

        self.configuration.set(MEDIA_SECTION, MEDIA_DIR,
                               self.__mediaDir if self.__mediaDir else '')

        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as configurationFile:
            self.configuration.write(configurationFile)


    def customiseRendering(self):
        """
        Apply custom rendering to the columns of the movieTreeView.

        This is a workaround for not (apparently?) being able to do this in
        Glade. We don't need to refer to the renderers elsewhere, so local
        variables are enough for our purposes.
        """

        # deal with justification of numeric columns.
        self.setXAlignment('durationRenderer')
        self.setXAlignment('dateRenderer')

        # set word wrapping on long text items (title, stars, other??)
        self.setColumnWordWrap('titleRenderer', 'titleColumn')
        self.setColumnWordWrap('directorRenderer', 'directorColumn')
        self.setColumnWordWrap('starsRenderer', 'starsColumn')
        self.setColumnWordWrap('genreRenderer', 'genreColumn')


    def setXAlignment(self, rendererName):
        """
        Set the renderer to display text right-aligned.
        """

        renderer = self.builder.get_object(rendererName)
        renderer.props.xalign = 1.0


    def setColumnWordWrap(self, rendererName, columnName):
        """
        Set word wrap on the given column.

        The word wrap policy is set in the renderer, using the minimum width of
        the column.
        """

        renderer = self.builder.get_object(rendererName)
        renderer.props.wrap_mode = Gtk.WrapMode.WORD
        renderer.props.wrap_width = \
            self.builder.get_object(columnName).get_min_width()


    def customiseFilter(self):
        """
        Set up the filter function.
        """

        self.movieTreeModelFilter.set_visible_func(self.makeMovieVisible,
                                                   self.filterMovieEntry)


    def makeMovieVisible(self, model, iteration, data):
        """
        This function is passed to the TreeModelFilter to decide which rows to
        display.
        """

        # when the filter data is empty expose everything
        if not data.get_text():
            return True

        # for series recursively check visibility of child nodes
        elif model[iteration][-1]:
            if model.iter_has_child(iteration):
                for n in range(model.iter_n_children(iteration)):
                    child_iter = model.iter_nth_child(iteration, n)
                    if self.makeMovieVisible(model, child_iter, data):
                        return True
            return False

        # apply the filter data
        else:
            filterText = data.get_text().lower()
            nonEmptyRow = False
            for value in model[iteration][:-1]:
                if isinstance(value, str):
                    if value:
                        nonEmptyRow = True
                        if filterText in value.lower():
                            return True  # match found for filter text
            return not nonEmptyRow  # allows empty entry to be visible


    def on_filterMovieEntry_changed(self, widget):
        """
        Handler for the filterMovieEntry widget.

        Update the data for the movieTreeModelFilter.
        """

        self.movieTreeModelFilter.refilter()


    def setDirty(self, dirty):
        """
        Set the dirty data flag.

        Ensure the save action can only be activated when the data is dirty.
        """

        if dirty != self.__dirty:
            self.__dirty = dirty
            self.fileSaveAction.set_sensitive(dirty)


    def chooseSaveFile(self, title, fileSelectionMode):
        """
        File selection dialog.

        The parameters determine whether the dialog is used for opening or
        saving the file. The chosen file is saved internally for future
        reference.
        Returns whether a satisfactory choice was made.
        """

        # select the stock button to use according to the selection mode
        okButtonType = None
        if fileSelectionMode == Gtk.FileChooserAction.OPEN:
            okButtonType = Gtk.STOCK_OPEN
        else:
            okButtonType = Gtk.STOCK_SAVE

        fileChooserDialog = Gtk.FileChooserDialog(title + '...',
                                                  self.window,
                                                  fileSelectionMode,
                                                  [Gtk.STOCK_CANCEL,
                                                   Gtk.ResponseType.CANCEL,
                                                   okButtonType,
                                                   Gtk.ResponseType.OK])
        response = fileChooserDialog.run()
        ok = response == Gtk.ResponseType.OK
        if ok:
            self.setFileName(fileChooserDialog.get_filename())
        fileChooserDialog.destroy()
        return ok


    def getFileName(self):
        return self.__filename


    def setFileName(self, filename):
        self.__filename = filename
        self.window.set_title(os.path.basename(self.__filename))
        self.saveConfiguration()


    def save(self, context):
        self.movieListIO.save()
        self.statusbar.push(context, 'Saved As: {}'.format(self.__filename))
        self.setDirty(False)


    # File menu and toolbar actions

    def on_fileNewAction_activate(self, widget):
        """
        Handler for the file new action.

        Clear out any existing data, start the tree from an empty data store.
        """

        context = self.statusbar.get_context_id('new')
        self.movieTreeStore.clear()
        self.setDirty(False)
        self.setFileName(None)
        self.statusbar.push(context, 'New: empty movie list created')


    def on_fileOpenAction_activate(self, widget):
        """
        Handler for the file open action.

        Clear existing data and load new data from a file.
        """

        context = self.statusbar.get_context_id('open')

        # choose a file
        if self.chooseSaveFile('Open', Gtk.FileChooserAction.OPEN):
            self.movieListIO.load()
            self.statusbar.push(context,
                                'Opened: {}'.format(self.__filename)
                                )
            self.setDirty(False)
        else:
            self.statusbar.push(context, 'Open: open aborted')


    def on_fileSaveAction_activate(self, widget):
        """
        Handler for the file save action.

        Save the current data in the file it came from. If no file can be
        identified, resort to the 'save as' action.
        """

        context = self.statusbar.get_context_id('save')
        if not self.__filename:
            self.on_fileSaveAsAction_activate(widget)
        else:
            self.save(context)


    def on_fileSaveAsAction_activate(self, widget):
        """
        Handler for the file save as action.

        Choose a file to save to, and save the data.
        """

        context = self.statusbar.get_context_id('save')

        # choose a file
        if self.chooseSaveFile('Save', Gtk.FileChooserAction.SAVE):
            self.save(context)
            self.saveConfiguration()
        else:
            self.statusbar.push(context, 'Save As: save aborted')


    def on_fileQuitAction_activate(self, widget):
        """
        Handler for the file quit action.

        This implementation just passes on responsibility to on_window_destroy().
        """

        self.on_window_destroy(widget)


    # Edit menu, toolbar and context actions

    def on_playAction_activate(self, widget):
        """
        Handler for the play action.

        Play the movie using an external application.
        """

        contextId = self.statusbar.get_context_id(PLAY)
        treeIndex, movie = self.getMovieOrSeriesFromSelection(contextId, PLAY)
        if not movie or isinstance(movie, MovieSeries):
            return

        # ensure media file is not blank
        filename = movie.media
        if not filename or not os.path.exists(filename):
            self.displaySelectMovieErrorMessage(contextId, PLAY)
            return

        # play the media
        # TODO: VLC  Media Player on *nix is assumed here
        system = subprocess.call('vlc "{}"'.format(filename), shell=True)
        self.statusbar.push(contextId, CONTEXT[PLAY][OK].format(filename))


    def on_addAction_activate(self, widget):
        """
        Handler for the movie add action. Add a new movie to the list.

        Displays a new empty movie in the edit dialog. If the movie information
        is changed, add the movie information to the list.
        """

        # the status bar context
        contextId = self.statusbar.get_context_id(ADD)

        # a selector to choose movie or series add
        dialog = Gtk.MessageDialog(self.window,
                                   Gtk.DialogFlags.MODAL,
                                   Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.NONE,
                                   'Add a Movie or a Movie Series?',
                                   )
        dialog.set_title('Choose Add Movie or Series')
        dialog.add_buttons('Movie', MOVIE_RESPONSE,
                           'Movie Series', MOVIE_SERIES_RESPONSE,
                           Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        selectionResponse = dialog.run()
        dialog.destroy()
        if selectionResponse == Gtk.ResponseType.CANCEL:
            return

        movieEntity = None
        response = ()
        if selectionResponse == MOVIE_SERIES_RESPONSE:
            movieEntity = MovieSeries()
            response = self.editMovieSeriesDialog(ADD, movieEntity, None, None)
        elif selectionResponse == MOVIE_RESPONSE:
            movieEntity = Movie()
            response = self.editMovieDialog(ADD, movieEntity, None, None)

        # update the model and display
        self.addMovieEntity(contextId, ADD, response[0],
                            None,
                            movieEntity, None,
                            response[1], response[2])


    def on_copyAction_activate(self, widget):
        """
        Handler for the movie copy action. Add a duplicate movie entity to the
        list.
        """

        # the status bar context
        contextId = self.statusbar.get_context_id(COPY)

        # select the movie/series to change
        treeIndex, movieEntity = self.getMovieOrSeriesFromSelection(contextId,
                                                                    COPY)
        if not movieEntity:
            return
        seriesIndex = None
        copiedMovieEntity = copiedSeriesIndex = None

        if isinstance(movieEntity, MovieSeries):
            copiedMovieEntity = MovieSeries.fromList(movieEntity.toList(), [])
        else:
            copiedSeriesIndex = self.findParentMovieSeries(treeIndex)
            copiedMovieEntity = Movie.fromList(movieEntity.toList())

        # update the model and display
        self.addMovieEntity(contextId, COPY, Gtk.ResponseType.OK,
                            None,
                            None, None,
                            copiedMovieEntity, copiedSeriesIndex)


    def on_editAction_activate(self, widget):
        """
        Handler for the movie edit action. Edit the selected movie.

        Takes the current selected movie and displays it in the edit dialog. If
        the movie information is changed, update the movie information in the
        list.
        """

        # context of status bar messages
        contextId = self.statusbar.get_context_id(EDIT)

        # select the movie/series to change
        treeIndex, movieEntity = self.getMovieOrSeriesFromSelection(contextId,
                                                                    EDIT)
        parentSeriesIndex = self.findParentMovieSeries(treeIndex)

        if not movieEntity:
            return
        response = ()

        # invoke the appropriate dialog
        if isinstance(movieEntity, MovieSeries):
             response = self.editMovieSeriesDialog(EDIT,
                                                   movieEntity,
                                                   treeIndex,
                                                   parentSeriesIndex)
        else:
             response = self.editMovieDialog(EDIT,
                                             movieEntity,
                                             treeIndex,
                                             parentSeriesIndex)

        # update the model and display
        self.editMovieEntity(contextId, EDIT, response[0],
                             treeIndex,
                             movieEntity, parentSeriesIndex,
                             response[1], response[2])


    def findParentMovieSeries(self, childMovieEntityIndex):
        """
        Get the treeIter of the parent series of a movie or series.
        """

        return (self.movieTreeStore.iter_parent(childMovieEntityIndex)
                if childMovieEntityIndex else None)


    def on_deleteAction_activate(self, widget):
        """
        Handler for the movie delete action. Delete the selected movie/series.

        Confirmation is required.
        """

        # context of status bar messages
        contextId = self.statusbar.get_context_id(DELETE)

        # get the current movie/series selection
        treeIndex, movieEntity = self.getMovieOrSeriesFromSelection(contextId,
                                                                    DELETE)
        if not movieEntity:
            return

        # invoke the confirmation dialog
        message = entityType = ''
        if isinstance(movieEntity, MovieSeries):
            entityType = 'Series'
            message = 'Confirm delete of {} {}'.format(entityType,
                                                       movieEntity.title)
        else:
            entityType = 'Movie'
            message = 'Confirm delete of {} {} ({})'.format(entityType,
                                                            movieEntity.title,
                                                            movieEntity.date)
        dialog = Gtk.MessageDialog(self.window,
                                   Gtk.DialogFlags.MODAL,
                                   Gtk.MessageType.WARNING,
                                   Gtk.ButtonsType.OK_CANCEL,
                                   message,
                                   )
        dialog.set_title('Delete {}'.format(entityType))
        response = dialog.run()
        dialog.destroy()

        # update the tree model
        self.deleteMovieEntity(contextId, DELETE, response,
                               treeIndex, movieEntity, None, None, None)


    def getMovieOrSeriesFromSelection(self, contextId, context):
        """
        Obtain a movie or series from the currently-selected treeView row.
        """

        # get the current movie selection
        parentModel, parentIter = self.movieTreeSelection.get_selected()

        treeModel = self.movieTreeStore
        treeIndex = getChildModelSelection(parentModel, parentIter)
        if treeIndex is None:
            self.displaySelectMovieErrorMessage(contextId, context)
            return None, None
        if treeModel[treeIndex][-1]:
            childIter = treeModel.iter_children(treeIndex)
            seriesList = self.movieListIO.extractMovieTreeAsList(childIter)
            return treeIndex, MovieSeries.fromList(treeModel[treeIndex],
                                                   seriesList)
        else:
            return treeIndex, Movie.fromList(treeModel[treeIndex])


    def displaySelectMovieErrorMessage(self, contextId, context):
        """
        Error message for functions that need a treeview selection.

        This started as a helper for edit/delete functions, but now it is also
        used by the play tool.
        """

        dialog = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL,
            Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK,
            CONTEXT[context][WARN].format(context))
        dialog.run()
        dialog.destroy()
        self.statusbar.push(contextId, CONTEXT[context][WARN].format(context))
        return


    def editMovieDialog(self, context, movie, treeIndex, parentSeriesIndex):
        """
        Invoke the dialog, return the edited movie and series information.
        """

        dialog = MovieEditDialog(context=context,
                                 parent=self.window,
                                 movie=movie,
                                 parentSeriesIndex=parentSeriesIndex,
                                 movieTreeStore=self.movieTreeStore,
                                 mediaDirectory=self.__mediaDir)
        response, editedMovie, editedSeriesIndex = dialog.run()
        if editedMovie.media:
            self.__mediaDir = os.path.dirname(editedMovie.media)
            self.saveConfiguration()
        return response, editedMovie, editedSeriesIndex


    def editMovieSeriesDialog(self, context, movieSeries, treeIndex,
                              parentSeriesIndex):
        """
        Invoke the dialog, return the edited series information.
        """

        dialog = MovieSeriesEditDialog(context=context,
                                       parent=self.window,
                                       series=movieSeries,
                                       parentSeriesIndex=parentSeriesIndex,
                                       movieTreeStore=self.movieTreeStore)
        response, editedSeries, editedSeriesIndex = dialog.run()
        return response, editedSeries, editedSeriesIndex


    @modifyMovieTreeStore
    def addMovieEntity(self, treeIndex,
                         originalMovieEntity, originalSeriesIndex,
                         modifiedMovieEntity, modifiedSeriesIndex):
        """
        Add a movie entity to the movieTreeStore.
        """

        if isinstance(modifiedMovieEntity, MovieSeries):
            print('Adding Series {} to parent series {}'.format(modifiedMovieEntity, modifiedSeriesIndex))
            self.movieListIO.appendSeriesToStore(modifiedMovieEntity,
                                                 modifiedSeriesIndex)
        else:
            print('Adding Movie {}'.format(modifiedMovieEntity))
            self.movieListIO.appendMovieToStore(modifiedMovieEntity,
                                                modifiedSeriesIndex)


    @modifyMovieTreeStore
    def editMovieEntity(self, treeIndex,
                          originalMovieEntity, originalSeriesIndex,
                          modifiedMovieEntity, modifiedSeriesIndex):
        """
        Edit a movie entity in the movieTreeStore.

        If the modified entity has been re-parented, append the new version to
        the new parent before deleting the old. Otherwise, change the entity's
        data in place.
        """

        if originalSeriesIndex == modifiedSeriesIndex:
            row = modifiedMovieEntity.toList()
            for col, value in enumerate(row):
                if value or (col == len(row) - 1):
                    self.movieTreeStore.set_value(treeIndex, col, value)
                else:
                    self.movieTreeStore.set_value(treeIndex, col, '')
        else:
            if isinstance(modifiedMovieEntity, MovieSeries):
                self.movieListIO.appendSeriesToStore(modifiedMovieEntity,
                                                     modifiedSeriesIndex)
                # TODO: Remove old children
                while self.movieTreeStore.has_children(treeIndex):
                    childIndex = self.movieTreeStore.iter_children()
                    self.movieTreeStore.delete(childIndex)

            else:
                self.movieListIO.appendMovieToStore(modifiedMovieEntity,
                                                    modifiedSeriesIndex)
            self.movieTreeStore.remove(treeIndex)


    @modifyMovieTreeStore
    def deleteMovieEntity(self, treeIndex,
                            originalMovieEntity, originalSeriesIndex,
                            modifiedMovieEntity, modifiedSeriesIndex):
        """
        Delete a movie entity from the movieTreeStore.

        If the entity is a series with children the orphaned movies are
        re-parented to the root before the entity is deleted.
        """

        if self.movieTreeStore.iter_has_child(treeIndex):
            self.reParentChildren(treeIndex, modifiedSeriesIndex)
        self.movieTreeStore.remove(treeIndex)


    def reParentChildren(self, seriesIter, newSeriesIter):
        """
        Take the children of a series to be deleted and re-parent them to the
        root, or another named series.
        """

        childIter = self.movieTreeStore.iter_children(seriesIter)
        while childIter:
            movie = Movie.fromList(self.movieTreeStore[childIter])
            self.movieTreeStore.remove(childIter)
            self.movieListIO.appendMovieToStore(movie, newSeriesIter)
            childIter = self.movieTreeStore.iter_children(seriesIter)


    # Tools menu actions

    def on_importAction_activate(self, widget):
        """
        Handler for the import action.

        Load csv data from a file.
        """

        context = self.statusbar.get_context_id('import')

        # choose a file
        if self.chooseSaveFile('Import', Gtk.FileChooserAction.OPEN):
            self.movieListIO.importCsv()
            self.statusbar.push(context,
                                'Imported: {}'.format(self.__filename)
                                )
            self.setDirty(True)
            self.__filename = None
        else:
            self.statusbar.push(context, 'Import: import aborted')


    # Help menu actions

    def on_aboutAction_activate(self, widget):
        """
        Handler for the about action. Display information about MovieList.
        """

        dialog = Gtk.AboutDialog()
        dialog.set_program_name('Movie List')
        dialog.set_version(VERSION)
        dialog.set_copyright('(c) Bob Bowles')
        dialog.set_comments("""
        A simple app to facilitate browsing lists of movies or videos.

        To import movie data,
        EITHER
        use xml (see examples)
        OR
        import from a text file as csv (see examples).
        """)
        dialog.set_website('http://bbclimited.com')
        dialog.set_website_label('Bob Bowles Web Site')
        dialog.set_license_type(Gtk.License.GPL_3_0)
        # dialog.set_logo('none')

        dialog.run()
        dialog.destroy()


    # Context menu actions

    def on_movieTreeView_button_press_event(self, widget, event):
        """
        Handler for mouse clicks on the tree view.

        Single L-click: change current selection (this is automatic).
        Double L-click: launch movie.
        R-click: Display the edit menu as a context popup.

        (Note: the edit menu is connected in Glade to the movieTreeView
        button_press_event as data, and swapped. So, the menu is passed to this
        handler as the widget, instead of the treeView.)
        """

        # double-click launches movie application
        if (event.button == Gdk.BUTTON_PRIMARY and
            event.type == Gdk.EventType._2BUTTON_PRESS):
            self.on_playAction_activate(widget)

        # right-click activates the context menu
        if event.button == Gdk.BUTTON_SECONDARY:
            widget.popup(None, None, None, None,
                         Gdk.BUTTON_SECONDARY, event.get_time())


    # main window event(s)

    def on_column_width_changed(self, widget, data):
        """
        Handler for resizing the columns.
        """

        self.saveConfiguration()


    def on_window_check_resize(self, widget):
        """
        Handler for resizing the window.

        Updates the configuration to save the new window size.
        """

        self.saveConfiguration()


    def on_window_destroy(self, widget):
        """
        Handler for closing window.

        A quick clean kill of the entire app.
        """

        # need to save any changes first.
        context = self.statusbar.get_context_id('Quit')
        if self.__dirty:
            dialog = Gtk.MessageDialog(
                                       self.window,
                                       Gtk.DialogFlags.MODAL,
                                       Gtk.MessageType.QUESTION,
                                       Gtk.ButtonsType.YES_NO,
                                       'There are unsaved changes. Save now?',
                                       )
            dialog.set_decorated(False)
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                self.on_fileSaveAction_activate(widget)

        self.statusbar.push(context, 'Destroying main window')
        Gtk.main_quit()




app = MovieList()
Gtk.main()
