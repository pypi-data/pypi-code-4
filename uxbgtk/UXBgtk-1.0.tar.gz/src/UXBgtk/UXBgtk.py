# Copyright (C) 2012 Bob Bowles <bobjohnbowles@gmail.com>
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

import random
import os
import ast
from gi.repository import Gtk, Gdk
from configparser import SafeConfigParser
from constants import UI_BUILD_FILE, UI_CSS_FILE, TOOL_SIZE, BUTTON_PAD
from constants import CONFIG_FILE
from constants import UI_SECTION, WINDOW_SIZE
from constants import GAME_PARAMS_SECTION, PBC, CONFIGURATION
from getImage import initializeImages, getImage, updateImage
from gridWindow import GridWindow
from gtkPause import pause



class UXBgtk:
    """
    The main game UI.
    """


    def __init__(self):
        """
        Initialize the UI.
        """

        self.initializeGUI()
        self.restoreConfiguration()

        self.window.show_all()


    def initializeGUI(self):
        """
        Load the main GUI elements from the .glade file.
        """

        self.builder = Gtk.Builder()
        self.builder.add_from_file(UI_BUILD_FILE)
        self.builder.connect_signals(self)

        # these are the toolbar widgets...

        # game start
        self.startButton = self.builder.get_object('startButton')
        self.startImage = getImage('Start')
        updateImage(self.startImage, 'Start', TOOL_SIZE)
        self.startButton.add(self.startImage)

        # hint request
        self.hintButton = self.builder.get_object('hintButton')
        self.hintImage = getImage('Hint')
        updateImage(self.hintImage, 'Hint', TOOL_SIZE)
        self.hintButton.add(self.hintImage)
        self.hintButton.set_sensitive(False)

        # periodic boundary condition toggle
        self.pbcButton = self.builder.get_object('pbcButton')
        self.pbcImage = getImage('PBC_Off')
        updateImage(self.pbcImage, 'PBC_Off', TOOL_SIZE)
        self.pbcButton.add(self.pbcImage)
        self.pbcButton.set_sensitive(True)

        # the configurationBox and its model
        self.configurations = self.builder.get_object('configurations')
        self.configurationBox = self.builder.get_object('configurationBox')

        # an alternative quit button
        self.resetButton = self.builder.get_object('resetButton')
        self.resetImage = getImage('Reset')
        updateImage(self.resetImage, 'Reset', TOOL_SIZE)
        self.resetButton.add(self.resetImage)

        # these are the status bar widgets
        self.exposedCount = self.builder.get_object('exposedCount')
        self.exposedLabel = self.builder.get_object('exposedLabel')
        self.flagCount = self.builder.get_object('flagCount')
        self.flagLabel = self.builder.get_object('flagLabel')

        # the game grid (blank for now)
        self.gridContainer = self.builder.get_object('gridContainer')
        self.gameGrid = None
        self.previousAllocation = self.gridContainer.get_allocation()

        # get references to the toolbar and status bar for size data.
        self.toolbar = self.builder.get_object('toolBox')
        self.statusbar = self.builder.get_object('statusBox')

        # get a reference to the main window itself and display the window
        self.window = self.builder.get_object('window')


    def restoreConfiguration(self):
        """
        Get the UI and game parameters from the last time the game was played.
        """

        self.configuration = SafeConfigParser()
        configList = self.configuration.read([CONFIG_FILE], encoding='utf-8')
        if configList:

            # restore the last saved window size
            if self.configuration[UI_SECTION][WINDOW_SIZE]:
                geometry = \
                    self.configuration[UI_SECTION][WINDOW_SIZE].split(',')
                x, y = (int(coord) for coord in geometry)
                self.window.resize(x, y)

            # restore the game parameters...

            # ...periodic boundary toggle
            if self.configuration[GAME_PARAMS_SECTION][PBC]:
                self.pbcButton.set_active(
                    ast.literal_eval(
                        self.configuration[GAME_PARAMS_SECTION][PBC]))

            # ...grid size and number of mines
            if self.configuration[GAME_PARAMS_SECTION][CONFIGURATION]:
                self.configurationBox.set_active(
                    int(self.configuration[GAME_PARAMS_SECTION][CONFIGURATION]))

        else:  # first time, create a vanilla configuration
            self.configuration.add_section(UI_SECTION)
            self.configuration.add_section(GAME_PARAMS_SECTION)
            self.saveConfiguration()


    def saveConfiguration(self):
        """
        Save any changes to the configuration options.
        """

        self.configuration.set(UI_SECTION, WINDOW_SIZE,
                               ', '.join(str(coord)
                                         for coord in self.window.get_size()))

        self.configuration.set(GAME_PARAMS_SECTION, PBC,
                               str(self.pbcButton.get_active()))
        self.configuration.set(GAME_PARAMS_SECTION, CONFIGURATION,
                               str(self.configurationBox.get_active()))

        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as configurationFile:
            self.configuration.write(configurationFile)


    def start(self):
        """
        Start a new game.
        """

        self.saveConfiguration()

        # reset the start button image
        updateImage(self.startImage, 'Start', TOOL_SIZE)

        # get the grid information from the configuration box.
        activeConfiguration = self.configurationBox.get_active_iter()
        cols, rows, nMines = tuple(self.configurations[activeConfiguration])[2:]

        mines = [True] * nMines
        mines.extend([False] * (cols * rows - nMines))
        random.shuffle(mines)

        # reset the status bar
        self.exposedCount.set_text('0')
        self.exposedLabel.set_text('/ ' + str(cols * rows - nMines))
        self.flagCount.set_text('0')
        self.flagLabel.set_text('/ ' + str(nMines))

        # destroy any pre-existing game
        if self.gameGrid != None: self.gameGrid.destroy()

        # 'force' re-size at the start of the game
        self.previousAllocation = None

        # make the new game
        self.gameGrid = GridWindow(parent=self,
                                   cols=cols, rows=rows, mines=mines)
        self.gridContainer.add_with_viewport(self.gameGrid)

        # configure the toolbar widgets sensitivity
        self.hintButton.set_sensitive(True)  # enable hints during a game
        self.pbcButton.set_sensitive(False)  # can't change pbc during a game
        self.configurationBox.set_button_sensitivity(Gtk.SensitivityType.OFF)

        # start the game
        self.gameGrid.start()
        self.gameGrid.giveHint()
        self.window.show_all()


    def on_window_destroy(self, widget):
        """
        Handler for closing window. A quick clean kill of the entire app.
        """

        Gtk.main_quit()


    def on_startButton_clicked(self, widget):
        """
        Handler for the start button.
        """

        self.start()


    def on_hintButton_clicked(self, widget):
        """
        Handler for the hint button.
        """

        self.gameGrid.giveHint()


    def on_pbcButton_toggled(self, widget):
        """
        Handler for the periodic boundary condition button.
        """

        if self.pbcButton.get_active():
            updateImage(self.pbcImage, 'PBC_On', TOOL_SIZE)
        else:
            updateImage(self.pbcImage, 'PBC_Off', TOOL_SIZE)


    def explodeGame(self):
        """
        Make an explosion effect on the screen as the grid is destroyed.
        """

        # obtain the size of the playing area
        size = (self.gridContainer.get_allocated_width(),
                self.gridContainer.get_allocated_height())

        # make the explosion flashImage
        flashImage = getImage('Explosion')
        updateImage(flashImage, 'Explosion', size)
        self.gridContainer.add_with_viewport(flashImage)

        # flash the explosion 5 times
        for i in range(5):

            # display the explosion
            updateImage(self.startImage, 'Click', TOOL_SIZE)
            flashImage.show()
            pause(100)  # wait 200ms without blocking the Gtk event loop

            # hide the explosion
            updateImage(self.startImage, 'Lose', TOOL_SIZE)
            flashImage.hide()
            pause(100)  # wait 200ms without blocking the Gtk event loop

        # ... then destroy the explosion image
        flashImage.destroy()


    def on_resetButton_clicked(self, widget):
        """
        Handler for the reset button. A theatrical way to kill the current
        game.
        """

        # get rid of the old game
        if self.gameGrid != None: self.gameGrid.destroy()

        self.explodeGame()

        # configure the toolbar widgets sensitivity
        self.hintButton.set_sensitive(False)
        self.pbcButton.set_sensitive(True)
        self.configurationBox.set_button_sensitivity(Gtk.SensitivityType.ON)


    def on_configurationBox_changed(self, widget):
        """
        Reset stuff that needs to be reset for creating the game grid.
        """

        pass  # no further action needed atm


    def on_window_check_resize(self, widget):
        """
        Handler for resizing the game grid images.
        """

        # do nothing if the game grid is not ready
        if not self.gameGrid: return

        # check to see if this is a real resize
        allocation = self.gridContainer.get_allocation()
        if (self.previousAllocation != None and
            allocation.width == self.previousAllocation.width and
            allocation.height == self.previousAllocation.height):
            return
        else:
            self.previousAllocation = allocation
            self.gameGrid.resize(allocation)
            self.saveConfiguration()


# load the image pixbuf cache
initializeImages()

# configure themed styles for the grid buttons
cssProvider = Gtk.CssProvider()
cssProvider.load_from_path(UI_CSS_FILE)
screen = Gdk.Screen.get_default()
styleContext = Gtk.StyleContext()
styleContext.add_provider_for_screen(screen, cssProvider,
                                     Gtk.STYLE_PROVIDER_PRIORITY_USER)

app = UXBgtk()
Gtk.main()

