#!/usr/bin/env python

# IPA Zounds, a sound change engine with support for the IPA.
# Copyright 2005 Jamie Norrish
#
# This file is part of IPA Zounds.
#
# IPA Zounds is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# IPA Zounds is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""PyGTK GUI for IPA Zounds."""

import codecs
import ConfigParser
import gettext
import glob
import os
import sys
from threading import Thread, Event
from xml.sax import saxutils

from ipazounds import __version__, locale_dir, ipa

gettext.install('ipazounds', locale_dir, unicode=1)

try:
    import pygtk
    if not sys.platform == 'win32':
        pygtk.require('2.0')
    import gtk, gobject, pango
except (ImportError, AssertionError):
    print _('PyGTK 2.8 is not available; please install it.').encode('utf-8')
    sys.exit(1)
if gtk.pygtk_version < (2, 8, 0):
    print _('Your version of PyGTK is too old; please install version 2.8 or later.').encode('utf-8')
    sys.exit(1)

APP_FULL_NAME = 'IPA Zounds Sound Change Engine'
APP_NAME = 'IPA Zounds'
# Create the script ListStore: first column is internal script
# name, second column is script display name.
script_store = gtk.ListStore(str, str)

class IPAZounds:

    """Class for main program and window."""

    def __init__ (self):
        # Initialise object variables.
        self.transform_event = TransformEvent(self)
        self.options = {}
        self.context_ids = {}
        self.gui = {}
        self.gui['main_window'] = gtk.Window(gtk.WINDOW_TOPLEVEL)
        # Get default options.
        default_options = self.get_default_options()
        # Get and apply user preferences.
        self.config = ConfigParser.ConfigParser(default_options)
        self.config_filename = os.path.expanduser('~/.ipazoundsrc')
        try:
            self.config.read(self.config_filename)
        except ConfigParser.Error:
            # If the configuration file is malformed, don't use it; it
            # will be overwritten with a valid file on exit.
            pass
        self.set_user_options()
        self.create_gui()
        self.results_page = 2
        self.connect_event_handlers()
        self.refresh_script_list()
        self.gui['main_window'].show()

    def create_gui (self):
        """Create and pack the widgets used in the application."""
        self.gui['main_window'].set_default_size(self.options['width'],
                                                 self.options['height'])
        self.gui['main_window'].set_title(APP_FULL_NAME)
        self.gui['mw_vbox'] = gtk.VBox(False, 1)
        self.gui['main_window'].add(self.gui['mw_vbox'])
        self.gui['menubar'] = self.create_menubar()
        self.gui['mw_vbox'].pack_start(self.gui['menubar'], False)
        self.gui['notebook'] = self.create_notebook()
        self.gui['mw_vbox'].pack_start(self.gui['notebook'])
        self.gui['statusbar_box'] = gtk.HBox()
        self.gui['statusbar'] = self.create_statusbar()
        self.gui['mw_vbox'].pack_end(self.gui['statusbar'], False)
        self.gui['mw_vbox'].show_all()
        # Create the dialogs.
        self.gui['preferences_dialog'] = PreferencesDialog(self)
        self.gui['about_dialog'] = self.create_about_dialog()
        self.gui['open_lexicon_dialog'] = self.create_open_lexicon_dialog()
        self.gui['open_rules_dialog'] = self.create_open_rules_dialog()
        self.gui['transformation_dialog'] = TransformationDialog(self)
        self.gui['progress_window'] = ProgressWindow(self)
        self.gui['properties_window'] = PropertiesWindow(self)
        save = gtk.FileChooserDialog(title=_('Save results'),
                                     action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                     buttons=(gtk.STOCK_CANCEL,
                                              gtk.RESPONSE_CANCEL,
                                              gtk.STOCK_SAVE,
                                              gtk.RESPONSE_OK))
        save.set_do_overwrite_confirmation(True)
        save.set_default_response(gtk.RESPONSE_OK)
        self.gui['save_results_dialog'] = save
        self.gui['alert_dialog'] = gtk.MessageDialog(self.gui['main_window'],
                                                     gtk.DIALOG_MODAL,
                                                     gtk.MESSAGE_WARNING,
                                                     gtk.BUTTONS_CLOSE)
        self.gui['error_dialog'] = gtk.MessageDialog(self.gui['main_window'],
                                                     gtk.DIALOG_MODAL,
                                                     gtk.MESSAGE_ERROR,
                                                     gtk.BUTTONS_CLOSE)

    def create_about_dialog (self):
        """Create, populate and return the AboutDialog widget."""
        dialog = gtk.AboutDialog()
        dialog.set_name(APP_NAME)
        dialog.set_version(__version__)
        dialog.set_comments('An IPA-aware sound change applier')
        dialog.set_copyright(u'Copyright \u00A9 2005 Jamie Norrish')
        dialog.set_license("""IPA Zounds is free software; you can redistribute
it and/or modify it under the terms of the GNU General
Public License as published by the Free Software 
Foundation; either version 2 of the License, or (at
your option) any later version.

IPA Zounds is distributed in the hope that it will
be useful, but WITHOUT ANY WARRANTY; without
even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General 
Public License along with this program; if not, write
to the Free Software Foundation, Inc., 51 Franklin St,
Fifth Floor, Boston, MA  02110-1301  USA""")
        dialog.set_website('http://zounds.artefact.org.nz/')
        dialog.set_authors(['Jamie Norrish <jamie@artefact.org.nz>'])
        dialog.set_transient_for(self.gui['main_window'])
        return dialog

    def create_menubar (self):
        """Create, populate and return the MenuBar widget."""
        entries = (
            ('FileMenu', None, _('_File')),
            ('HelpMenu', None, _('_Help')),
            ('OpenLexicon', gtk.STOCK_OPEN, _('Open _Lexicon...'),
             _('<control>L'), None, self.open_file_dialog),
            ('OpenRules', gtk.STOCK_OPEN, _('Open _Rules...'),
             _('<control>R'), None, self.open_file_dialog),
            ('TransformMenu', None, _('_Transform Lexicon')),
            ('SimpleTransformation', gtk.STOCK_EXECUTE,
             _('_Simple Transformation'), _('<control>T'), None,
             self.transform_event.transform),
            ('ModifiedTransformation', gtk.STOCK_EXECUTE,
             _('_Modified Transformation'), _('<control>M'), None,
             self.transform_event.transform),
            ('SaveResults', gtk.STOCK_SAVE, _('_Save Results...'),
             _('<control>S'), None, self.save_results),
            ('Properties', gtk.STOCK_PROPERTIES, _('Proper_ties'),
             _('<alt>Return'), None, self.open_properties_window),
            ('Preferences', gtk.STOCK_PREFERENCES, _('_Preferences'),
             _('<control>P'), None, self.open_preferences_dialog),
            ('Quit', gtk.STOCK_QUIT, _('_Quit'), _('<control>Q'),
             None, self.on_main_window_delete_event),
            ('About', gtk.STOCK_ABOUT, _('_About'), None, None,
             self.open_about_dialog)
            )
        ui_info = """<ui><menubar name='MenuBar'><menu action='FileMenu'>
        <menuitem action='OpenLexicon'/>
        <menuitem action='OpenRules'/>
        <menu action='TransformMenu'>
        <menuitem action='SimpleTransformation'/>
        <menuitem action='ModifiedTransformation'/>
        </menu>
        <separator/>
        <menuitem action='SaveResults'/>
        <separator/>
        <menuitem action='Properties'/>
        <separator/>
        <menuitem action='Preferences'/>
        <separator/>
        <menuitem action='Quit'/>
        </menu>
        <menu action='HelpMenu'>
        <menuitem action='About'/>
        </menu></menubar></ui>"""
        actions = gtk.ActionGroup('Actions')
        actions.add_actions(entries)
        ui = gtk.UIManager()
        ui.insert_action_group(actions, 0)
        self.gui['main_window'].add_accel_group(ui.get_accel_group())
        ui.add_ui_from_string(ui_info)
        # Desensitise actions that cannot be used on startup.
        self.gui['transform_menu'] = actions.get_action('TransformMenu')
        self.gui['save_action'] = actions.get_action('SaveResults')
        self.gui['modified_transformation_action'] = actions.get_action('ModifiedTransformation')
        self.gui['properties_action'] = actions.get_action('Properties')
        self.gui['transform_menu'].set_sensitive(False)
        self.gui['save_action'].set_sensitive(False)
        self.gui['properties_action'].set_sensitive(False)
        return ui.get_widget('/MenuBar')

    def create_notebook (self):
        """Create, populate and return the notebook."""
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        notebook.set_border_width(2)
        self.gui['lexicon_window'] = LexiconWindow(self)
        self.gui['rules_window'] = RulesWindow(self)
        self.gui['results_window'] = ResultsWindow(self)
        self.gui['lexicon_tab_label'] = gtk.Label(_('Lexicon'))
        self.gui['rules_tab_label'] = gtk.Label(_('Rules'))
        self.gui['results_tab_label'] = gtk.Label(_('Results'))
        notebook.append_page(self.gui['lexicon_window'],
                             self.gui['lexicon_tab_label'])
        notebook.append_page(self.gui['rules_window'],
                             self.gui['rules_tab_label'])
        notebook.append_page(self.gui['results_window'],
                             self.gui['results_tab_label'])
        return notebook

    def create_open_lexicon_dialog (self):
        """Create, populate and return the open lexicon dialog."""
        file_filter = gtk.FileFilter()
        file_filter.set_name(_('Lexicon files'))
        file_filter.add_pattern('*.lex')
        return OpenFileDialog(_('Open lexicon file'), self.gui['main_window'],
                              file_filter)

    def create_open_rules_dialog (self):
        """Create, populate and return the open lexicon dialog."""
        file_filter = gtk.FileFilter()
        file_filter.set_name(_('Rules files'))
        file_filter.add_pattern('*.sc')
        return OpenFileDialog(_('Open rules file'), self.gui['main_window'],
                              file_filter)

    def create_statusbar (self):
        """Create, populate and return the statusbar."""
        statusbar = gtk.Statusbar()
        context_descriptions = ('config', 'results', 'lexicon', 'rules')
        for desc in context_descriptions:
            self.context_ids[desc] = statusbar.get_context_id(desc)
        return statusbar

    def connect_event_handlers (self):
        """Set up the event handlers."""
        self.gui['main_window'].connect('delete-event',
                                        self.on_main_window_delete_event)
        self.gui['notebook'].connect('switch-page', self.on_switch_page_event)

    def get_default_options (self):
        """Return a dictionary of the default options."""
        options = {}
        # Get the default font.
        context = self.gui['main_window'].create_pango_context()
        options['font'] = context.get_font_description().to_string()
        # file_dir is the directory from which lexicon and rules files
        # are selected.
        options['file_dir'] = os.path.abspath('.')
        # scripts_dir is the directory from which user-defined script
        # files are read.
        options['scripts_dir'] = os.path.abspath('.')
        options['output_format'] = 'both'
        options['full_format'] = 'False'
        # Size of main window.
        options['width'] = '450'
        options['height'] = '600'
        return options

    def get_script_names (self):
        """Return a list of script names available to the application."""
        # IPA and X-SAMPA support is built in.
        script_names = [('ipa', 'IPA'), ('xsampa', 'X-SAMPA')]
        filename_pattern = os.path.join(self.options['scripts_dir'], '*.orth')
        ipa.converter.set_data_path(self.options['scripts_dir'])
        for filename in glob.glob(filename_pattern):
            script_name = os.path.splitext(os.path.basename(filename))
            script_names.append((script_name[0], script_name[0]))
        return script_names

    def on_main_window_delete_event (self, *args):
        """Quit the application."""
        # Save user settings.
        self.save_settings()
        gtk.main_quit()
        return False

    def on_switch_page_event (self, notebook, page, page_number):
        """Event handler for change of notebook page."""
        page = notebook.get_nth_page(page_number)
        self.set_statusbar_message(page)
        return True

    def open_about_dialog (self, *args):
        """Open the About dialog."""
        self.gui['about_dialog'].run()
        return True

    def open_file_dialog (self, action):
        """Open a lexicon file."""
        action_name = action.get_name()
        if action_name == 'OpenLexicon':
            dialog = self.gui['open_lexicon_dialog']
        elif action_name == 'OpenRules':
            dialog = self.gui['open_rules_dialog']
        dialog.set_current_folder(self.options['file_dir'])
        if dialog.run() == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
            script_names = dialog.get_script()
            self.options['file_dir'] = os.path.abspath(os.path.dirname(filename))
            dialog.hide()
            try:
                file_handle = codecs.open(filename, 'rU', 'utf-8')
                lines = file_handle.readlines()
                # Remove BOM if there is one
                lines[0] = lines[0].lstrip(unicode(codecs.BOM_UTF8,
                                                   'utf-8'))
            except IOError:
                self.show_message('error', _('Failed to open file: %s') %
                                  sys.exc_info()[1])
                self.open_file_dialog(action)
            except UnicodeDecodeError:
                self.show_message('error',
                                  _('Failed to read file (not UTF-8): %s') %
                                  sys.exc_info()[1])
                self.open_file_dialog(action)
            except IndexError:
                # File is completely empty.
                self.show_message('error', _('File is empty'))
                self.open_file_dialog(action)
            else:
                file_handle.close()
                if action_name == 'OpenLexicon':
                    words = ipa.compile_words(lines, script_names[0])
                    window = self.gui['lexicon_window']
                    try:
                        window.gs_words(words)
                    except ipa.convert.ConvertError, err:
                        window.clear_items()
                        self.show_message('error', str(err))
                        self.open_file_dialog(action)
                        return True
                    window.filename = os.path.basename(filename)
                elif action_name == 'OpenRules':
                    try:
                        window = self.gui['rules_window']
                        rules_parser = ipa.RulesParser(lines, script_names[0])
                        window.display_rules(rules_parser)
                    except (ipa.convert.ConvertError,
                            ipa.zounds.InvalidRulesFileError), err:
                        self.show_message('error', str(err))
                        window.clear_items()
                        self.open_file_dialog(action)
                        return True
                    except ipa.zounds.InvalidRuleError, err:
                        error = saxutils.escape('%s' % err)
                        self.show_message('error', _('Invalid rule in file: <span font_desc="%s">%s</span>') \
                                          % (self.options['font'], error))
                        self.open_file_dialog(action)
                        return True
                    else:
                        window.filename = os.path.basename(filename)
                page_number = self.gui['notebook'].page_num(window)
                self.set_statusbar_message(window)
                self.gui['notebook'].set_current_page(page_number)
                if self.gui['lexicon_window'].gs_words() and \
                   self.gui['rules_window'].get_rules():
                    self.gui['transform_menu'].set_sensitive(True)
        else:
            dialog.hide()
        return True

    def open_preferences_dialog (self, action):
        """Open the preferences dialog."""
        self.gui['preferences_dialog'].show()
        return True

    def open_properties_window (self, action):
        """Open the properties window."""
        self.gui['properties_window'].run()
        self.gui['properties_window'].hide()
        return True

    def redisplay (self):
        """Redisplay the lexicon, rules and results, so that new
        option values are used."""
        self.gui['lexicon_window'].redisplay()
        self.gui['rules_window'].redisplay()
        self.gui['results_window'].redisplay()
        self.gui['preferences_dialog'].set_label_font(self.options['font'])

    def refresh_script_list (self):
        """Refresh the list of available scripts."""
        scripts = self.get_script_names()
        script_store.clear()
        for script in scripts:
            script_store.append(script)
        self.gui['preferences_dialog'].gui['script_selector'].set_active(0)
        self.gui['open_lexicon_dialog'].script_selector.set_active(0)
        self.gui['open_rules_dialog'].script_selector.set_active(0)

    def save_results (self, action):
        """Save current results to file."""
        results = self.gui['results_window'].results
        if not results:
            self.show_message('alert', _('There are no results to save.'))
            return True
        dialog = self.gui['save_results_dialog']
        if dialog.run() == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
            dialog.hide()
            try:
                save_file = codecs.EncodedFile(open(filename, 'w'), 'utf-8')
                save_file.write(self.gui['properties_window'].get_data())
                save_file.write(results)
                save_file.close()
            except IOError:
                self.show_message('error', _('Failed to save results: %s') %
                                  sys.exc_info()[1])
                self.save_results(action)
        else:
            dialog.hide()
        return True

    def save_settings (self):
        """Save the user settings."""
        try:
            config_file = open(self.config_filename, 'wU')
        except IOError:
            return
        (width, height) = self.gui['main_window'].get_size()
        self.options['height'] = height
        self.options['width'] = width
        for key, value in self.options.items():
            self.config.set('DEFAULT', key, value)
        self.config.write(config_file)
        config_file.close()

    def set_statusbar_message (self, page):
        """Set the message for notebook page."""
        if page == self.gui['lexicon_window']:
            context_id = self.context_ids['lexicon']
            message = page.filename
        elif page == self.gui['rules_window']:
            context_id = self.context_ids['rules']
            message = page.filename
        elif page == self.gui['results_window']:
            context_id = self.context_ids['results']
            if self.gui['results_window'].results:
                message = _('%s transformed using %s') % \
                          (self.gui['results_window'].lexicon_filename,
                           self.gui['results_window'].rules_filename)
            else:
                message = ''
        else:
            return
        self.gui['statusbar'].pop(context_id)
        self.gui['statusbar'].push(context_id, message)

    def set_user_options (self):
        """Set the user-specified options"""
        self.options['file_dir'] = self.config.get('DEFAULT', 'file_dir')
        self.options['scripts_dir'] = self.config.get('DEFAULT', 'scripts_dir')
        self.options['output_format'] = self.config.get('DEFAULT',
                                                        'output_format')
        self.options['full_format'] = self.config.getboolean('DEFAULT',
                                                             'full_format')
        self.options['font'] = self.config.get('DEFAULT', 'font')
        self.options['width'] = self.config.getint('DEFAULT', 'width')
        self.options['height'] = self.config.getint('DEFAULT', 'height')

    def show_message (self, message_type, message):
        """Show an message dialog with message."""
        if message_type == 'alert':
            dialog = self.gui['alert_dialog']
        elif message_type == 'error':
            dialog = self.gui['error_dialog']
        dialog.set_markup(message)
        dialog.run()
        dialog.hide()


class ScriptSelector (gtk.HBox):
    """Class for the script selector."""

    def __init__ (self, model, label):
        """Arguments:
        model -- TreeModel object
        label -- string label to accompany combobox

        """
        self.gui = {}
        self.model = model
        gtk.HBox.__init__(self)
        self.set_spacing(12)
        self.gui['label'] = gtk.Label(label)
        self.gui['label'].set_alignment(0.0, 0.5)
        self.pack_start(self.gui['label'], False)
        self.gui['label'].show()
        self.gui['combobox'] = gtk.ComboBox(self.model)
        cell = gtk.CellRendererText()
        self.gui['combobox'].pack_start(cell, True)
        self.gui['combobox'].add_attribute(cell, 'text', 1)
        self.pack_start(self.gui['combobox'])
        self.gui['combobox'].show()

    def get_current_script (self):
        """Return a tuple of the internal and external names of the
        currently selected script."""
        tree_iter = self.gui['combobox'].get_active_iter()
        return (self.model.get_value(tree_iter, 0),
                self.model.get_value(tree_iter, 1))

    def get_active (self):
        """Return the index of the active item in the combobox."""
        return self.gui['combobox'].get_active()

    def set_active (self, index):
        """Set the ComboBox's active item to that specified by index."""
        self.gui['combobox'].set_active(index)
    

class NotebookWindow (gtk.ScrolledWindow):
    """Class for the scrolled windows within the notebook."""

    def __init__ (self, root):
        """Arguments:
        root -- IPAZounds object

        """
        self.root = root
        self.gui = {}
        self.filename = ''
        gtk.ScrolledWindow.__init__(self)
        # Only show scrollbars when needed
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        # Create text area
        textview = gtk.TextView()
        self.gui['textbuffer'] = gtk.TextBuffer()
        textview.set_buffer(self.gui['textbuffer'])
        self.add(textview)
        textview.show()
        textview.set_left_margin(10)
        textview.set_right_margin(20)
        textview.set_editable(False)
        textview.set_cursor_visible(False)
        self.gui['textview'] = textview

    def set_font (self):
        """Set the font for the window."""
        font = self.root.options['font']
        self.gui['textview'].modify_font(pango.FontDescription(font))


class LexiconWindow (NotebookWindow):
    """Class for the lexicon window."""

    def __init__ (self, root):
        NotebookWindow.__init__(self, root)
        self.words = []

    def gs_words (self, words=None):
        """Get or set the list of words. If words are provided,
        display them.

        Arguments:
        words -- optional list of ipa.Word objects

        """
        if words:
            self.set_font()
            self.words = words
            word_forms = [word.get_form('display') for word in self.words]
            self.gui['textbuffer'].set_text('\n'.join(word_forms))
        return self.words

    def clear_items (self):
        """Remove all words."""
        self.words = None

    def redisplay (self):
        """Redisplay words."""
        self.gs_words(self.words)
        

class ResultsWindow (NotebookWindow):
    """Class for the results window."""

    def __init__ (self, root):
        NotebookWindow.__init__(self, root)
        self.root = root
        self.results = ''
        self.lexicon_filename = ''
        self.rules_filename = ''
        self.words = []
        self.reverse = False

    def redisplay (self):
        """Redisplay results."""
        self.set_words(self.words)

    def set_filenames (self):
        """Set and return the lexicon and rules filenames using the
        current values."""
        self.lexicon_filename = self.root.gui['lexicon_window'].filename
        self.rules_filename = self.root.gui['rules_window'].filename
        return self.lexicon_filename, self.rules_filename

    def set_words (self, words):
        """Set the list of words which are the basis of the results.

        Arguments:
        words -- list of ipa.Word objects

        """
        self.set_font()
        self.words = words
        if self.root.options['output_format'] == 'history' and self.reverse:
            ipa.display.set_output_format('both')
            self.results = '\n'.join(ipa.display.get_formatted_output(self.words))
            ipa.display.set_output_format('history')
        else:
            self.results = '\n'.join(ipa.display.get_formatted_output(self.words))
        self.gui['textbuffer'].set_text(self.results)

    def append_word (self, word):
        """Append word to the results.

        Arguments:
        word -- ipa.Word object
        reverse -- Boolean indicating reverse transformation or not
        
        """
        self.set_font()
        self.words.append(word)
        # Reverse applier results cannot be rendered with the show
        # rules option, so change it for this call.
        if self.root.options['output_format'] == 'history' and self.reverse:
            ipa.display.set_output_format('both')
            text = '\n'.join(ipa.display.get_formatted_output([word])) + '\n'
            ipa.display.set_output_format('history')
        else:
            text = '\n'.join(ipa.display.get_formatted_output([word])) + '\n'
        self.results = self.results + text
        text_iter = self.gui['textbuffer'].get_end_iter()
        self.gui['textbuffer'].insert(text_iter, text)
        self.root.set_statusbar_message(self)
        self.root.gui['notebook'].set_current_page(self.root.results_page)
        return False
        

class RulesWindow (NotebookWindow):
    """Class for the rules window."""

    def __init__ (self, root):
        NotebookWindow.__init__(self, root)
        self.rules_parser = None

    def get_rules (self, start_date=None, end_date=None, dialects=None):
        """Return a list of rules."""
        if self.rules_parser:
            return self.rules_parser.get_rules(start_date, end_date, dialects)
        return []

    def get_phonotactics (self):
        """Return a dictionary of phonotactic variables."""
        if self.rules_parser:
            return self.rules_parser.get_phonotactics()
        return {}

    def display_rules (self, rules_parser):
        """Display the contents of rules_parser."""
        self.rules_parser = rules_parser
        if not self.rules_parser:
            return
        section_lines = self.rules_parser.get_lines()
        self.set_font()
        formatted_lines = []
        for section in ('Dialects', 'Groups', 'Persistent', 'Rules',
                        'Phonotactics'):
            lines = section_lines[section]
            if lines:
                formatted_lines.append(self.compile_section_lines(section,
                                                                  lines))
        self.gui['textbuffer'].set_text('\n'.join(formatted_lines))

    def compile_section_lines (self, section, lines):
        """Return a list of formatted lines in section."""
        full_format = self.root.options['full_format']
        formatted_lines = ['', '%s' % section]
        original_indent = 5
        indent = original_indent
        for line in lines:
            if line.__class__ == ipa.Rule:
                joiner = '\n%s' % (indent * ' ')
                rule_form = joiner.join(line.get_formatted(full_format))
                formatted_lines.append('%s%s' % (indent * ' ', rule_form))
            elif type(line) == type(()):
                if line[0].__class__ == ipa.Rule:
                    joiner = '\n%s' % (indent * ' ')
                    rule_form = joiner.join(line[0].get_formatted(full_format))
                    dialects = self.format_dialects(line[1])
                    formatted_lines.append('%s%s' % (indent * ' ', rule_form +
                                                     dialects))
                else:
                    dialects = self.format_dialects(line[1])
                    formatted_lines.append('%s%s' % (indent * ' ', line[0] +
                                                     dialects))
            elif type(line) == type(1):
                # This is a date, so increase the indent for subsequent lines.
                formatted_lines.append('%s%s' % (original_indent * ' ', line))
                indent = original_indent * 2
            else:
                formatted_lines.append('%s%s' % (indent * ' ', line))
        return '\n'.join(formatted_lines)

    def format_dialects (self, dialects):
        """Return formatted string from list of dialects."""
        return '    %s' % ', '.join(dialects)

    def redisplay (self):
        """Redisplay rules."""
        self.display_rules(self.rules_parser)

    def clear_items (self):
        """Remove all rules."""
        self.rules_parser = None
        

class OpenFileDialog (gtk.FileChooserDialog):
    """Class for open file dialogs, containing standard file chooser
    with script selector."""

    def __init__ (self, title, parent, file_filter):
        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN,
                   gtk.RESPONSE_OK)
        gtk.FileChooserDialog.__init__(self, title, parent, buttons=buttons)
        self.add_filter(file_filter)
        # Add filter for all files.
        file_filter = gtk.FileFilter()
        file_filter.set_name(_('All files'))
        file_filter.add_pattern('*')
        self.add_filter(file_filter)
        self.script_selector = ScriptSelector(script_store,
                                              _('File written using script:'))
        self.script_selector.show()
        self.set_extra_widget(self.script_selector)

    def get_script (self):
        """Return a tuple of the names of the selected script."""
        return self.script_selector.get_current_script()


class PreferencesDialog (gtk.Dialog):
    """Class for preferences dialog."""

    def __init__ (self, root):
        self.root = root
        self.gui = {}
        title = _('%s Preferences') % APP_NAME
        flags = gtk.DIALOG_DESTROY_WITH_PARENT
        buttons = (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
        gtk.Dialog.__init__(self, title, self.root.gui['main_window'], flags,
                            buttons)
        self.set_border_width(12)
        self.set_has_separator(False)
        self.connect('response', self.on_response_event)
        self.connect('delete-event', self.on_delete_event)
        self.vbox.set_spacing(18)
        self.create_options()
        self.previous_script = 0 # Index of the ComboBox

    def create_options (self):
        """Create the widgets that specify the various options."""
        font_vbox = self.create_font_section()
        self.vbox.pack_start(font_vbox, False)
        script_vbox = self.create_script_section()
        self.vbox.pack_start(script_vbox, False)
        result_vbox = self.create_result_section()
        self.vbox.pack_start(result_vbox, False)
        rules_vbox = self.create_rules_section()
        self.vbox.pack_start(rules_vbox, False)
        self.vbox.show_all()

    def create_font_section (self):
        """Create and return the widget containing the font section."""
        vbox = gtk.VBox(False, 12)
        heading = gtk.Label()
        heading.set_markup('<b>%s</b>' % _('Font'))
        heading.set_alignment(0.0, 0.5)
        vbox.pack_start(heading, False)
        hbox = gtk.HBox(False)
        label = gtk.Label(_('Data font:'))
        label.set_padding(12, 0)
        hbox.pack_start(label, False)
        selector = gtk.FontButton(self.root.options['font'])
        selector.connect('font-set', self.on_font_set_event)
        hbox.pack_end(selector)
        vbox.pack_start(hbox, False)
        return vbox

    def create_script_section (self):
        """Create and return the widget containing the script section."""
        vbox = gtk.VBox(False, 12)
        heading = gtk.Label()
        heading.set_markup('<b>%s</b>' % _('Script'))
        heading.set_alignment(0.0, 0.5)
        vbox.pack_start(heading, False)
        hbox = gtk.HBox(False)
        label = gtk.Label(_('Scripts directory:'))
        label.set_padding(12, 0)
        hbox.pack_start(label, False)
        file_chooser = gtk.FileChooserButton(_('Select a directory'))
        file_chooser.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        file_chooser.set_current_folder(self.root.options['scripts_dir'])
        file_chooser.connect('current-folder-changed',
                             self.on_current_folder_changed_event)
        file_filter = gtk.FileFilter()
        file_filter.set_name(_('Script files'))
        file_filter.add_pattern('*.orth')
        file_chooser.add_filter(file_filter)
        hbox.pack_end(file_chooser)
        vbox.pack_start(hbox, False)
        selector = ScriptSelector(script_store, _('Data script:'))
        selector.gui['label'].set_padding(12, 0)
        vbox.pack_start(selector, False)
        selector.set_spacing(0)
        selector.gui['combobox'].connect('changed',
                                         self.on_script_changed_event)
        self.gui['script_selector'] = selector
        return vbox

    def create_result_section (self):
        """Create and return the widget containing the result format
        section."""
        vbox = gtk.VBox(False, 12)
        heading = gtk.Label()
        heading.set_markup('<b>%s</b>' % _('Result format'))
        heading.set_alignment(0.0, 0.5)
        vbox.pack_start(heading, False)
        table = gtk.Table(rows=4, columns=2, homogeneous=False)
        table.set_border_width(12)
        both_button = gtk.RadioButton(None, _('Show both words'))
        # Make this the default (for those occasions when the config
        # file has a bogus value).
        both_button.set_active(True)
        self.gui['both_button_label'] = gtk.Label(u'l\N{LATIN SMALL LETTER OPEN E}ct\N{LATIN SMALL LETTER OPEN O}\N{LATIN SMALL LETTER TURNED R} \N{RIGHTWARDS ARROW} l\N{LATIN SMALL LETTER OPEN E}it\N{LATIN SMALL LETTER OPEN O}\N{LATIN SMALL LETTER TURNED R}')
        self.gui['both_button_label'].set_use_markup(True)
        y_alignment = self.gui['both_button_label'].get_alignment()[1]
        self.gui['both_button_label'].set_alignment(0, y_alignment)
        self.gui['both_button_label']
        table.attach(both_button, 0, 1, 0, 1)
        table.attach(self.gui['both_button_label'], 1, 2, 0, 1, xpadding=20)
        bracket_button = gtk.RadioButton(both_button,
                                         _('Bracket original word'))
        self.gui['bracket_button_label'] = gtk.Label(u'l\N{LATIN SMALL LETTER OPEN E}it\N{LATIN SMALL LETTER OPEN O}\N{LATIN SMALL LETTER TURNED R} [l\N{LATIN SMALL LETTER OPEN E}ct\N{LATIN SMALL LETTER OPEN O}\N{LATIN SMALL LETTER TURNED R}]')
        self.gui['bracket_button_label'].set_use_markup(True)
        y_alignment = self.gui['bracket_button_label'].get_alignment()[1]
        self.gui['bracket_button_label'].set_alignment(0, y_alignment)
        table.attach(bracket_button, 0, 1, 1, 2)
        table.attach(self.gui['bracket_button_label'], 1, 2, 1, 2, xpadding=20)
        rules_button = gtk.RadioButton(both_button, _('Show rules'))
        self.gui['rules_button_label'] = gtk.Label(u'l\N{LATIN SMALL LETTER OPEN E}ct\N{LATIN SMALL LETTER OPEN O}\N{LATIN SMALL LETTER TURNED R} \N{RIGHTWARDS ARROW} l\N{LATIN SMALL LETTER OPEN E}it\N{LATIN SMALL LETTER OPEN O}\N{LATIN SMALL LETTER TURNED R} ( k \N{RIGHTWARDS ARROW} i / [\N{MINUS SIGN}back\N{MINUS SIGN}central+syllabic]_t )')
        self.gui['rules_button_label'].set_use_markup(True)
        y_alignment = self.gui['rules_button_label'].get_alignment()[1]
        self.gui['rules_button_label'].set_alignment(0, y_alignment)
        table.attach(rules_button, 0, 1, 2, 3)
        table.attach(self.gui['rules_button_label'], 1, 2, 2, 3, xpadding=20)
        omit_button = gtk.RadioButton(both_button, _('Omit original word'))
        self.gui['omit_button_label'] = gtk.Label(u'l\N{LATIN SMALL LETTER OPEN E}it\N{LATIN SMALL LETTER OPEN O}\N{LATIN SMALL LETTER TURNED R}')
        self.gui['omit_button_label'].set_use_markup(True)
        y_alignment = self.gui['omit_button_label'].get_alignment()[1]
        self.gui['omit_button_label'].set_alignment(0, y_alignment)
        self.set_label_font(self.root.options['font'])
        table.attach(omit_button, 0, 1, 3, 4)
        table.attach(self.gui['omit_button_label'], 1, 2, 3, 4, xpadding=20)
        self.result_button_group = ((both_button, 'both'),
                                    (bracket_button, 'bracket_input'),
                                    (rules_button, 'history'),
                                    (omit_button, 'omit_input'))
        for button_set in self.result_button_group:
            if self.root.options['output_format'] == button_set[1]:
                button_set[0].set_active(True)
                ipa.display.set_output_format(button_set[1])
            button_set[0].connect('toggled', self.on_result_button_toggled,
                                  button_set[1])
        vbox.pack_start(table, False)
        return vbox

    def create_rules_section (self):
        """Create and return the widget containing the rules format
        section."""
        vbox = gtk.VBox(False, 12)
        heading = gtk.Label()
        heading.set_markup('<b>%s</b>' % _('Rules format'))
        heading.set_alignment(0.0, 0.5)
        vbox.pack_start(heading, False)
        full_format_button = gtk.CheckButton(_('Full format (requires monospace font)'))
        full_format_button.set_border_width(12)
        if self.root.options['full_format']:
            full_format_button.set_active(True)
        ipa.display.set_full_format(full_format_button.get_active())
        vbox.pack_start(full_format_button, False)
        full_format_button.connect('toggled',
                                   self.on_full_format_button_toggled)
        return vbox

    def on_current_folder_changed_event (self, file_chooser):
        """Event handler for current folder changed event."""
        self.root.options['scripts_dir'] = file_chooser.get_current_folder()
        self.root.refresh_script_list()
        return True

    def on_delete_event (self, *args):
        """Event handler for delete event."""
        self.hide()
        return True
        
    def on_font_set_event (self, button):
        """Event handler for font-set event."""
        self.root.options['font'] = button.get_font_name()
        self.root.redisplay()
        return True

    def on_full_format_button_toggled (self, button):
        """Event handler for toggled event on the full format button."""
        state = button.get_active()
        self.root.options['full_format'] = state
        ipa.display.set_full_format(state)
        self.root.redisplay()
        return True

    def on_response_event (self, dialog, response_id):
        """Event handler for response event."""
        if response_id == gtk.RESPONSE_CLOSE:
            self.hide()
        return True

    def on_result_button_toggled (self, button, value):
        """Event handler for toggled event on output format buttons."""
        if button.get_active():
            self.root.options['output_format'] = value
            ipa.display.set_output_format(value)
            self.root.redisplay()

    def on_script_changed_event (self, combobox):
        """Event handler for change of script selection."""
        selector = self.gui['script_selector']
        script = selector.get_current_script()[0]
        ipa.display.set_current_script(script)
        try:
            self.root.redisplay()
        except ipa.convert.ConvertError, err:
            self.root.show_message('error', str(err))
            selector.set_active(self.previous_script)
            script = selector.get_current_script()[0]
            ipa.display.set_current_script(script)
        else:
            self.previous_script = selector.get_active()
        return True

    def set_label_font (self, font):
        """Set the font for the labels which use IPA characters."""
        for label in (self.gui['both_button_label'],
                      self.gui['bracket_button_label'],
                      self.gui['rules_button_label'],
                      self.gui['omit_button_label']):
            text = label.get_text()
            label.set_label('<span font_desc="%s">%s</span>' % (font, text))


class TransformationDialog (gtk.Dialog):
    """Class for modified transformation dialog."""

    def __init__ (self, root):
        self.root = root
        self.gui = {}
        title = _('Modified Transformation')
        flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | \
                gtk.DIALOG_NO_SEPARATOR
        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK,
                   gtk.RESPONSE_OK)
        gtk.Dialog.__init__(self, title, self.root.gui['main_window'], flags,
                            buttons)
        self.set_border_width(12)
        self.set_has_separator(False)
        self.vbox.set_spacing(18)
        self.date_store = gtk.ListStore(int)
        self.dialect_store = gtk.ListStore(str, str)
        self.create_options()

    def create_options (self):
        """Create the widgets that specify the various options."""
        restriction_vbox = self.create_restriction_section()
        self.vbox.pack_start(restriction_vbox, False)
        reverse_vbox = self.create_reverse_section()
        self.vbox.pack_start(reverse_vbox, False)
        self.vbox.show_all()

    def create_restriction_section (self):
        """Create and return the widget containing the restriction
        section."""
        vbox = gtk.VBox(False, 12)
        heading = gtk.Label()
        heading.set_markup('<b>%s</b>' % _('Restrictions'))
        heading.set_alignment(0.0, 0.5)
        vbox.pack_start(heading, False)
        hbox = gtk.HBox(False)
        label = gtk.Label(_('_Start date:'))
        label.set_padding(12, 0)
        hbox.pack_start(label, False)
        self.gui['start_date_combobox'] = gtk.ComboBox(self.date_store)
        cell = gtk.CellRendererText()
        self.gui['start_date_combobox'].pack_start(cell, True)
        self.gui['start_date_combobox'].add_attribute(cell, 'text', 0)
        hbox.pack_end(self.gui['start_date_combobox'])
        vbox.pack_start(hbox, False)
        hbox = gtk.HBox(False)
        label = gtk.Label(_('_End date:'))
        label.set_padding(12, 0)
        hbox.pack_start(label, False)
        self.gui['end_date_combobox'] = gtk.ComboBox(self.date_store)
        cell = gtk.CellRendererText()
        self.gui['end_date_combobox'].pack_start(cell, True)
        self.gui['end_date_combobox'].add_attribute(cell, 'text', 0)
        hbox.pack_end(self.gui['end_date_combobox'])
        vbox.pack_start(hbox, False)
        hbox = gtk.HBox(False)
        label = gtk.Label(_('_Dialect:'))
        label.set_padding(12, 0)
        hbox.pack_start(label, False)
        self.gui['dialect_combobox'] = gtk.ComboBox(self.dialect_store)
        cell = gtk.CellRendererText()
        self.gui['dialect_combobox'].pack_start(cell, True)
        self.gui['dialect_combobox'].add_attribute(cell, 'text', 1)
        hbox.pack_end(self.gui['dialect_combobox'])
        vbox.pack_start(hbox, False)
        return vbox

    def create_reverse_section (self):
        """Create and return the widget containing the reverse section."""
        vbox = gtk.VBox(False, 12)
        heading = gtk.Label()
        heading.set_markup('<b>%s</b>' % _('Direction'))
        heading.set_alignment(0.0, 0.5)
        vbox.pack_start(heading, False)
        hbox = gtk.HBox(False)
        self.gui['direction_button'] = gtk.CheckButton(_('_Reverse'))
        self.gui['direction_button'].set_border_width(12)
        hbox.pack_start(self.gui['direction_button'], False)
        vbox.pack_start(hbox, False)
        return vbox

    def get_dialect (self):
        """Return the selected dialect."""
        tree_iter = self.gui['dialect_combobox'].get_active_iter()
        if tree_iter:
            return self.dialect_store.get_value(tree_iter, 0)
        return None

    def get_direction (self):
        """Return the selected transformation direction."""
        return self.gui['direction_button'].get_active()

    def get_end_date (self):
        """Return the selected end date."""
        tree_iter = self.gui['end_date_combobox'].get_active_iter()
        if tree_iter:
            return self.date_store.get_value(tree_iter, 0)
        return None

    def get_start_date (self):
        """Return the selected start date."""
        tree_iter = self.gui['start_date_combobox'].get_active_iter()
        if tree_iter:
            return self.date_store.get_value(tree_iter, 0)
        return None

    def populate_data (self):
        """Populate the list stores with the latest information."""
        rules_parser = self.root.gui['rules_window'].rules_parser
        self.date_store.clear()
        self.dialect_store.clear()
        number_dates = -1
        for date in rules_parser.get_dates():
            self.date_store.append([date])
            number_dates = number_dates + 1
        self.dialect_store.append(('', _('No dialect')))
        dialects = [(value, key) for key, value in \
                    rules_parser.get_dialects().items()]
        dialects.sort()
        for name, abbreviation in dialects:
            self.dialect_store.append((abbreviation, name))
        self.gui['start_date_combobox'].set_active(0)
        self.gui['end_date_combobox'].set_active(number_dates)
        self.gui['dialect_combobox'].set_active(0)

    def run (self):
        """Run the dialog."""
        self.populate_data()
        return gtk.Dialog.run(self)

        
class TransformEvent:
    """Class to handle transformations."""

    watch_cursor = gtk.gdk.Cursor(gtk.gdk.WATCH)

    def __init__ (self, root):
        self.root = root
        self.thread = None
        self.words = []

    def transform (self, action):
        """Transform words using rules."""
        start_date, end_date, dialect, reverse = (None, None, None, False)
        if action == self.root.gui['modified_transformation_action']:
            dialog = self.root.gui['transformation_dialog']
            response = dialog.run()
            if response == gtk.RESPONSE_OK:
                dialog.hide()
                start_date = dialog.get_start_date()
                end_date = dialog.get_end_date()
                dialect = dialog.get_dialect()
                reverse = dialog.get_direction()
                phonotactics = self.root.gui['rules_window'].get_phonotactics()
            else:
                dialog.hide()
                return
        try:
            rules = self.root.gui['rules_window'].get_rules(start_date,
                                                            end_date, dialect)
        except ipa.zounds.ZoundsError, err:
            self.handle_error(str(err))
            return
        self.words = self.root.gui['lexicon_window'].gs_words()
        if not rules:
            self.handle_error(_('The restricted rules set contains no rules'))
            return
        self.root.gui['main_window'].window.set_cursor(self.watch_cursor)
        try:
            if reverse:
                sce = ipa.ReverseSoundChange(rules, phonotactics)
                self.root.gui['results_window'].reverse = True
            else:
                sce = ipa.SoundChange(rules)
                self.root.gui['results_window'].reverse = False
        except ipa.zounds.ZoundsError, err:
            self.handle_error(str(err))
            return
        self.root.gui['results_window'].set_words([])
        lexicon_filename, rules_filename = self.root.gui['results_window'].set_filenames()
        data = {'lexicon': lexicon_filename, 'rules': rules_filename,
                'start_date': start_date, 'end_date': end_date,
                'dialect': dialect, 'direction': reverse}
        self.root.gui['properties_window'].set_data(data)
        # Allow for menu actions which depend on there being results.
        self.root.gui['save_action'].set_sensitive(True)
        self.root.gui['properties_action'].set_sensitive(True)
        # Run the tranformation in a separate thread.
        self.thread = TransformThread(self.root, sce, self.words)
        self.thread.start()
        response = self.root.gui['progress_window'].run(len(self.words))
        self.root.gui['progress_window'].hide()
        if response == gtk.RESPONSE_CANCEL:
            self.thread.join()
        elif self.thread.exception:
            self.handle_error(self.thread.exception)
            return
        self.end_transformation()

    def handle_error (self, error_message):
        """Handle any errors that occurred during the transformation."""
        self.end_transformation()
        self.root.show_message('error', error_message)

    def end_transformation (self):
        """End the transformation."""
        self.thread = None
        # Reset the cursor.
        self.root.gui['main_window'].window.set_cursor(None)
        self.words = None


class TransformThread (Thread):

    def __init__ (self, root, sce, words):
        Thread.__init__(self)
        self.root = root
        self.sce = sce
        self.words = words
        self.exception = None
        self.cancel_event = Event()

    def run (self):
        """Run the transformation in the thread."""
        try:
            for word in self.sce.transform_lexicon(self.words):
                if self.cancel_event.isSet():
                    break
                gobject.idle_add(self.update_gui, word)
        except (ipa.zounds.ZoundsError, ipa.convert.ConvertError), err:
            self.exception = str(err)
        self.root.gui['progress_window'].response(gtk.RESPONSE_NONE)

    def join (self, timeout=None):
        """Stop the thread."""
        self.cancel_event.set()
        Thread.join(self, timeout)

    def update_gui (self, word):
        """Update the GUI with the results in word."""
        reverse = self.sce.__class__ == ipa.ReverseSoundChange
        self.root.gui['results_window'].append_word(word)
        self.root.gui['progress_window'].increment()
        return False
    

class ProgressWindow (gtk.Dialog):
    """Class for the progress window."""

    def __init__ (self, root):
        title = _('Transforming lexicon')
        flags = gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR
        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        gtk.Dialog.__init__(self, title, root.gui['main_window'], flags,
                            buttons)
        self.vbox.set_spacing(18)
        self.set_border_width(12)
        self.total_words = 0
        self.transformed_words = 0
        self.gui = {}
        self.create_gui()
        self.vbox.show_all()

    def create_gui (self):
        """Add the text and progressbar to the dialog."""
        label = gtk.Label()
        label.set_markup('<span weight="bold" size="larger">Transforming lexicon</span>')
        self.vbox.pack_start(label, False)
        self.gui['progressbar'] = gtk.ProgressBar()
        self.gui['progressbar'].set_ellipsize(pango.ELLIPSIZE_END)
        self.vbox.pack_start(self.gui['progressbar'], False)

    def run (self, total_words):
        """Set the progress bar text and number to an initial state
        for a transformation."""
        self.total_words = total_words
        self.transformed_words = -1
        self.increment()
        return gtk.Dialog.run(self)

    def increment (self):
        """Increment the number of words transformed, and adjust the
        text and fraction of the progress bar accordingly."""
        self.transformed_words = self.transformed_words + 1.0
        fraction = self.transformed_words / self.total_words
        self.gui['progressbar'].set_fraction(fraction)
        self.gui['progressbar'].set_text('%d of %d words transformed' %
                                         (int(self.transformed_words),
                                          self.total_words))
        # Send a response if we've reached the end; while the
        # transformation thread should do this itself, it sometimes
        # doesn't when the transformation finishes before the dialog
        # gets the chance to run.
        if self.transformed_words == self.total_words:
            self.response(gtk.RESPONSE_NONE)


class PropertiesWindow (gtk.Dialog):
    """Class for the properties window."""

    def __init__ (self, root):
        self.root = root
        title = _('Results Properties')
        flags = gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR
        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        gtk.Dialog.__init__(self, title, self.root.gui['main_window'], flags,
                            buttons)
        self.set_border_width(12)
        self.gui = {}
        self.create_gui()
        self.vbox.show_all()
        self.data = {}

    def create_gui (self):
        """Create the GUI components of the window."""
        table = gtk.Table(rows=6, columns=2)
        label = gtk.Label()
        label.set_markup('<b>%s:</b>' % _('Lexicon file'))
        label.set_alignment(0.0, 0.5)
        table.attach(label, 0, 1, 0, 1)
        self.gui['lexicon'] = gtk.Label()
        self.gui['lexicon'].set_alignment(0.0, 0.5)
        table.attach(self.gui['lexicon'], 1, 2, 0, 1, xpadding=20)
        label = gtk.Label()
        label.set_markup('<b>%s:</b>' % _('Rules file'))
        label.set_alignment(0.0, 0.5)
        table.attach(label, 0, 1, 1, 2)
        self.gui['rules'] = gtk.Label()
        self.gui['rules'].set_alignment(0.0, 0.5)
        table.attach(self.gui['rules'], 1, 2, 1, 2, xpadding=20)
        label = gtk.Label()
        label.set_markup('<b>%s:</b>' % _('Direction'))
        label.set_alignment(0.0, 0.5)
        table.attach(label, 0, 1, 2, 3)
        self.gui['direction'] = gtk.Label()
        self.gui['direction'].set_alignment(0.0, 0.5)
        table.attach(self.gui['direction'], 1, 2, 2, 3, xpadding=20)
        label = gtk.Label()
        label.set_markup('<b>%s:</b>' % _('Start date'))
        label.set_alignment(0.0, 0.5)
        table.attach(label, 0, 1, 3, 4)
        self.gui['start_date'] = gtk.Label()
        self.gui['start_date'].set_alignment(0.0, 0.5)
        table.attach(self.gui['start_date'], 1, 2, 3, 4, xpadding=20)
        label = gtk.Label()
        label.set_markup('<b>%s:</b>' % _('End date'))
        label.set_alignment(0.0, 0.5)
        table.attach(label, 0, 1, 4, 5)
        self.gui['end_date'] = gtk.Label()
        self.gui['end_date'].set_alignment(0.0, 0.5)
        table.attach(self.gui['end_date'], 1, 2, 4, 5, xpadding=20)
        label = gtk.Label()
        label.set_markup('<b>%s:</b>' % _('Dialect'))
        label.set_alignment(0.0, 0.5)
        table.attach(label, 0, 1, 5, 6)
        self.gui['dialect'] = gtk.Label()
        self.gui['dialect'].set_alignment(0.0, 0.5)
        table.attach(self.gui['dialect'], 1, 2, 5, 6, xpadding=20)
        self.vbox.pack_start(table, False)

    def get_data (self):
        """Return the properties as comments."""
        comments = []
        comments.append('### %s' % _('Results File'))
        comments.append('#')
        comments.append('# %s: %s' % (_('Lexicon file'), self.data['lexicon']))
        comments.append('# %s: %s' % (_('Rules file'), self.data['rules']))
        comments.append('#')
        comments.append('# %s: %s' % (_('Direction'), self.data['direction']))
        comments.append('#')
        comments.append('# %s: %s' % (_('Start date'), self.data['start_date']))
        comments.append('# %s: %s' % (_('End date'), self.data['end_date']))
        comments.append('# %s: %s' % (_('Dialect'), self.data['dialect']))
        comments.append('\n')
        return '\n'.join(comments)

    def set_data (self, data):
        """Set the values of the properties from the dictionary data."""
        # Create a copy of the data dictionary with the values
        # normalised.
        self.data['lexicon'] = data['lexicon']
        self.data['rules'] = data['rules']
        if data['direction']:
            self.data['direction'] = _('Reverse')
        else:
            self.data['direction'] = _('Forwards')
        self.data['start_date'] = str(data['start_date'])
        self.data['end_date'] = str(data['end_date'])
        self.data['dialect'] = str(data['dialect'])
        if not self.data['dialect']:
            self.data['dialect'] = _('None')
        for key, value in self.data.items():
            self.gui[key].set_text(value)


if __name__ == '__main__':
    try:
        gobject.threads_init()
    except:
        print _("The GUI requires that your installation of PyGTK have threading enabled, but sadly it doesn't.").encode('utf-8')
        sys.exit(1)
    ipa_zounds = IPAZounds()
    gtk.main()
