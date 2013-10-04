#!/usr/bin/env python

'''

    Bat-man - YouTube video batch downloader
    Copyright (C) 2013 ElegantMonkey

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see [http://www.gnu.org/licenses/].

'''

# Avoid Windows of blowing up my plans.
import sys

WINDOWS = sys.platform.startswith("win")

import batman.batch_downloader as bd
from gi.repository import Gtk, GObject, Gdk

if not WINDOWS:
    from gi.repository import Notify

import threading
import gettext
# For some awkward reason, gettext module doesn't works with Gtk, because it's a C library
# Locale, instead, works.
import locale
import os
import configparser
import gc
from multiprocessing import freeze_support

GObject.threads_init()

if getattr(sys, "frozen", False):
    current_path = os.path.join(os.path.dirname(os.path.realpath(sys.executable)), "batman")
else:
    current_path = os.path.dirname(os.path.realpath(__file__))

APP = "batman"
DIR = os.path.join(current_path, "locale")
if WINDOWS:
    os.environ["LANG"] = locale.getdefaultlocale()[0]

# Don't know if it's just with me, but, under Windows, this doesn't works.
try:
    locale.bindtextdomain(APP, DIR)
except:
    pass

gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
gettext.install(APP, DIR)

def prepare_builder_for_translation(builder):
    builder.set_translation_domain(APP)

class Options(object):
    def __init__(self):
        self.cfgParser = configparser.ConfigParser()
        try:
            self.cfgParser.read("options.cfg")
        except IOError:
            pass
        self.quality = self.cfgParser.getint("Options", "quality", fallback=360)
        # Ranges from 0 to 9 - LAME specific.
        self.VBRquality = self.cfgParser.getint("Options", "VBRquality", fallback=2)
        
        # Alright, what happens here: If there is a folder set in the options,
        # check if it exists. If it does, set it as the default folder. If it
        # doesn't, set the user's home as the default folder, but instruct the program
        # to NOT OVERWRITE the original config unless it's changed.
        self._defaultFolderChanged = False
        self._originalDefaultFolder = self.cfgParser.get("Options", "defaultFolder", fallback="")
        if os.path.isdir(self._originalDefaultFolder):
            self._defaultFolder = self._originalDefaultFolder
        else:
            self._defaultFolder = os.path.expanduser("~")
    
    @property
    def defaultFolder(self):
        return self._defaultFolder
    
    @defaultFolder.setter
    def defaultFolder(self, value):
        self._defaultFolder = value
        self._defaultFolderChanged = True
    
    def write(self):
        self.cfgParser["Options"] = {}
        self.cfgParser["Options"]["quality"] = str(self.quality)
        self.cfgParser["Options"]["VBRquality"] = str(self.VBRquality)
        if self._defaultFolderChanged:
            self.cfgParser["Options"]["defaultFolder"] = self._defaultFolder
        with open("options.cfg", "w") as f:
            self.cfgParser.write(f)

class OptionsDialog(object):
    def __init__(self, options):
        self.options = options
        self.builder = Gtk.Builder()
        prepare_builder_for_translation(self.builder)
        self.builder.add_from_file(os.path.join(current_path, "glade", "optionsDialog.glade"))
        self.dialog = self.builder.get_object("optionsDialog")
        self.videoqualityComboBox = self.builder.get_object("videoqualityComboBox")
        self.conversionqualityScale = self.builder.get_object("conversionqualityScale")
        # Smart-ass solution.
        qualityIndex = [240, 360, 480, 720, 1080].index(self.options.quality)
        self.videoqualityComboBox.set_active(qualityIndex)
        self.conversionqualityScale.set_value(self.options.VBRquality)
        self.builder.connect_signals(self)
    
    def onClose(self, *args):
        quality = int(self.videoqualityComboBox.get_active_text()[0:-1])
        self.options.quality = quality
        self.options.VBRquality = int(self.conversionqualityScale.get_value())
        self.options.write()

class AboutDialog(object):
    def __init__(self):
        self.builder = Gtk.Builder()
        prepare_builder_for_translation(self.builder)
        self.builder.add_from_file(os.path.join(current_path, "glade", "aboutDialog.glade"))
        self.dialog = self.builder.get_object("aboutDialog")

class InsertLinksDialog(object):
    def __init__(self):
        self.builder = Gtk.Builder()
        prepare_builder_for_translation(self.builder)
        self.builder.add_from_file(os.path.join(current_path, "glade", "insertDialog.glade"))
        self.dialog = self.builder.get_object("insertDialog")
        self.builder.connect_signals(self)
        self.links = self.builder.get_object("links")

    def add_new_links(self):
        response = self.dialog.run()
        
        if response == 0: # Insert response
            bounds = self.links.get_buffer().get_bounds()
            if len(bounds) != 0:
                start, end = bounds
                text = self.links.get_buffer().get_text(start, end, True)
                
                return text.split("\n")
            else:
                return None
        else:
            return None
    
    def hide(self):
        self.dialog.hide()
            
    def onInsertClicked(self, *args):
        # What to do?
        pass
    
    def onCancelClicked(self, *args):
        pass

# All-in-caps-for-emphasis
# THIS THREAD DOESN'T DOWNLOADS ANYTHING
# ONLY ADDS VIDEOS TO THE QUEUE AND THAT'S ALL.
class HelperThread(threading.Thread):
    def __init__(self, marshaller):
        super().__init__()
        self.marshaller = marshaller
        self.event = threading.Event()
    
    def add_video_to_download(self, url, outfolder, quality, VBRquality=2):
        self.marshaller.add_video_to_download(url, outfolder, quality, VBRquality)
        self.event.set()
    
    def run(self):
        self.marshaller.event_starter(self.event)
    
    def quit(self):
        self.marshaller.event_starter_quit = True
        self.event.set()
		
class InserterThread(threading.Thread):
    def __init__(self, helperThread):
        super().__init__()
        self.helperThread = helperThread
        self.queue = []
        self._quit = False
        self.event = threading.Event()
        # For status bar
        # When added_element is None, there is no element being processed.
        # This, plus len(queue) == 0, indicates the queue is empty.
        self.message_callback = lambda self, added_element: None
    
    def add_video_to_download(self, *args, **kwargs):
        self.queue.append([args, kwargs])
        self.event.set()
    
    def run(self):
        while not self._quit:
            self.event.wait()
            self.message_callback(self, None)
            for element in self.queue:
                self.helperThread.add_video_to_download(*element[0],
                                                        **element[1])
                self.message_callback(self, element)
            self.queue.clear()
            self.message_callback(self, None)
            self.event.clear()
    
    def quit(self):
        self._quit = True
        self.event.set()

class MainWindow(object):
    def __init__(self, marshaller):
        # Threads
        self.helperThread = HelperThread(marshaller)
        self.inserterThread = InserterThread(self.helperThread)
        self.inserterThread.message_callback = self.on_inserter_thread_callback
        
        # Gtk
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.builder = Gtk.Builder()
        prepare_builder_for_translation(self.builder)
        self.builder.add_from_file(os.path.join(current_path, "glade", "mainWindow.glade"))
        self.window = self.builder.get_object("mainWindow")
        self.insertLinksDialog = InsertLinksDialog()
        self.aboutDialog = AboutDialog()
        self.options = Options()
        self.optionsDialog = OptionsDialog(self.options)
        self.destination = self.options.defaultFolder
        self.folderChoose = Gtk.FileChooserDialog(
                                title=_("Choose destination folder"),
                                action=Gtk.FileChooserAction.SELECT_FOLDER,
                                buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK,
                                         Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        
        #                              DownloadAndEncode, title, state
        self.liststore = self.builder.get_object("videoListStore")
        self.marshaller = marshaller
        self.marshaller.on_video_start_download = lambda x, y: GObject.idle_add(lambda *args: self.refresh_marshaller(), None)
        self.marshaller.on_video_progress = lambda *args: GObject.idle_add(lambda *args: self.refresh_download_progress(), None)
        self.marshaller.on_video_start_encoding = lambda x, y, z: GObject.idle_add(lambda *args: self.refresh_marshaller(), None)
        self.marshaller.on_video_finish = lambda x, y: GObject.idle_add(self.on_video_finish, x, y)
        self.helperThread.start()
        self.inserterThread.start()
        
        self.treeview = self.builder.get_object("videoTreeView")
        cellRendererTitle = Gtk.CellRendererText()
        columnTitle = Gtk.TreeViewColumn(_("Title"), cellRendererTitle, text=1)
        cellRendererState = Gtk.CellRendererText()
        columnState = Gtk.TreeViewColumn(_("State"), cellRendererState, text=2)
        self.treeview.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        self.treeview.connect("drag-data-received", self.onTreeViewDragDataRecieved)
        self.treeview.drag_dest_add_text_targets()
        self.clear_list = self.builder.get_object("clearList")
        self.clear_list.set_sensitive(False)
        self.set_destination = self.builder.get_object("setDestination")
        
        self.treeview.append_column(columnTitle)
        self.treeview.append_column(columnState)
        
        self.popupTreeView = self.builder.get_object("popupTreeView")
        
        self.progressbar = self.builder.get_object("progressbar")
        self.download_progressbar = self.builder.get_object("downloadProgressbar")
        self.download_progressbar.set_show_text(True)
        self.download_progressbar.set_text("")
        self.general_data = self.builder.get_object("generalData")
        self.statusbar = self.builder.get_object("statusbar")
        ctx_id = self.statusbar.get_context_id("inserter")
        self.statusbar.push(ctx_id, _("Ready!"))
        
        self.refresh_marshaller()
        self.reset_destination()
        self.reset_data_label()
        
        self.builder.connect_signals(self)
        
        # LibNotify
        if not WINDOWS:
            self.notification = Notify.Notification.new("Bat-man", "",
                                                        os.path.join(current_path, "glade", "batman-logo.png"))
    
    def on_inserter_thread_callback(self, inserter, element):
        size = len(self.inserterThread.queue)
        # WTF?
        ctx_id = self.statusbar.get_context_id("inserter")
        
        if element == None and size > 0:
            self.statusbar.push(ctx_id, _("Adding videos... ({}/{})").format(0, size))
        elif element == None and size == 0:
            self.statusbar.push(ctx_id, _("Ready!"))
        else:
            i = self.inserterThread.queue.index(element)        
            self.statusbar.push(ctx_id, _("Adding videos... ({}/{})").format(i, size))
    
    def on_video_finish(self, marshaller, video):
        self.refresh_marshaller()
        self.refresh_download_progress()
        if not WINDOWS:
            finished = len(self.marshaller.finished)
            total = len(self.marshaller.all)
            string = _("\"{}\" finished. ({}/{})").format(video.video.title, finished, total)             
            self.notification.update("Bat-man", string, os.path.join(current_path, "glade", "batman-logo.png"))
            self.notification.show()

    def reset_data_label(self):
        self.general_data.set_text(_("- {} video(s)\n"\
        "- Destination: {}").format(len(self.marshaller.all), self.destination))
    
    def reset_destination(self):
        for i in self.marshaller.all:
            i.set_outfolder(self.destination)
    
    # DIRTY DIRTY DIRTY DIRTY DIRTY DIRTY GAAH GAAH
    def refresh_marshaller(self):
        progress = 0
        size = len(self.marshaller.all)
        self.liststore.clear()
        for video in self.marshaller.all:
            state = self.marshaller.find_state_of_video(video)
            if state == bd.DownloadAndEncodeMarshaller.NON_EXISTANT:
                progress += 0
                self.liststore.append([video, video.video.title, _("Non existant")])
            elif state == bd.DownloadAndEncodeMarshaller.PENDING:
                progress += 0
                self.liststore.append([video, video.video.title, _("Pending")])
            elif state == bd.DownloadAndEncodeMarshaller.DOWNLOADING:
                progress += 1/3/size
                self.liststore.append([video, video.video.title, _("Downloading")])
            elif state == bd.DownloadAndEncodeMarshaller.ENCODING:
                progress += 2/3/size
                self.liststore.append([video, video.video.title, _("Encoding")])
            elif state == bd.DownloadAndEncodeMarshaller.FINISHED:
                progress += 1/size
                self.liststore.append([video, video.video.title, _("Finished")])
            elif state == bd.DownloadAndEncodeMarshaller.NOT_FOUND:
                progress += 0
                self.liststore.append([video, video.video.title, _("Not found")])
        self.progressbar.set_fraction(progress)
        
        # Should we be able to activate clear list?
        if len(self.marshaller.finished) > 0:
            self.clear_list.set_sensitive(True)
    
    def refresh_download_progress(self):
        size = len(self.marshaller.downloading)
        progress = 0.0
        speed = 0
        for video in self.marshaller.downloading:
            # May happen it be None, there is a small-to-medium gap between the
            # start of the download function(where it is set as downloading by
            # the marshaller) and the current downloading.
            if video.download_progress != None:
                progress += video.download_progress[2]/size
                speed += video.download_progress[3]
        self.download_progressbar.set_fraction(progress)
        if size != 0:
            self.download_progressbar.set_text("{:.2%} @ {:.0f} KBps".format(progress, speed/size))
        else:
            self.download_progressbar.set_text("")
    
    def onItemInsertActivate(self, *args):
        links = self.insertLinksDialog.add_new_links()
        self.insertLinksDialog.hide()
        if links != None:
            for l in links:
                if l.strip() != "":
                    self.inserterThread.add_video_to_download(l,
                                                          self.destination,
                                                          self.options.quality,
                                                          self.options.VBRquality)
            self.refresh_marshaller()
            self.reset_data_label()
    
    def onCloseCalled(self, *args):
        Gtk.main_quit()
        self.inserterThread.quit()
        self.helperThread.quit()
        self.inserterThread.join()
        self.helperThread.join()
        del self.inserterThread
        del self.helperThread
        del self.marshaller
        # Kill thread? Need to see this. Or sys.exit
    
    def onItemAboutActivate(self, *args):
        self.aboutDialog.dialog.run()
        self.aboutDialog.dialog.hide()
    
    def onItemOptionsActivate(self, *args):
        self.optionsDialog.dialog.run()
        self.optionsDialog.dialog.hide()
            
    def onSetDestinationClicked(self, *args):
        response = self.folderChoose.run()
        self.folderChoose.hide()
        if response == Gtk.ResponseType.OK:
            self.destination = self.folderChoose.get_filename()
            self.options.defaultFolder = self.destination
            self.options.write()
            self.reset_destination()
            self.reset_data_label()
    
    def onClearListClicked(self, *args):
        for video in self.marshaller.finished:
            try:
                self.marshaller.finished.remove(video)
                self.marshaller.all.remove(video)
            except:
                pass
        
        self.refresh_marshaller()
    
    def onTreeViewClicked(self, widget, event):
        # 3 == right click
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.popupTreeView.popup(None, None, None, None, event.button, event.time)
    
    def onTreeViewPaste(self, *args):
        content = self.clipboard.wait_for_text()
        
        if content != None:
            for line in content.split("\n"):
                self.inserterThread.add_video_to_download(line, self.destination,
                                                          self.options.quality,
                                                          self.options.VBRquality)
    
    def onTreeViewDragDataRecieved(self, widget, drag_context, x, y, data, info, time):
        links = data.get_text().split("\n")
        for line in links:
            self.inserterThread.add_video_to_download(line, self.destination,
                                                      self.options.quality,
                                                      self.options.VBRquality)

def main():
    if not WINDOWS:
        Notify.init("Bat-man")
    freeze_support()
    marshaller = bd.DownloadAndEncodeMarshaller()
    w = MainWindow(marshaller)
    w.window.show_all()
    Gtk.main()
    del marshaller
    # Calling the Garbage Collector manually isn't good, but this makes
    # the temporary files be excluded.
    gc.collect()

if __name__ == "__main__":
    main()

