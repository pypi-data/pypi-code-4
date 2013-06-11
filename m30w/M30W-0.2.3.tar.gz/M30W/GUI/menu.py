#This file is part of the M30W software.
#Copyright (C) 2012-2013 M30W developers.
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import subprocess
import wx
from threading import Thread
from wx.lib.dialogs import messageDialog as message
from M30W.debug import debug, print_not_implemented_functions
from errorConsole import ErrorConsole
from preferences import PreferencesDialog
import dialogs
from M30W import media, runtime, IO
from M30W.config import config


NORMAL = 'normal'
SEPARATOR = 'separator'
CHECK = 'checkitem'


class Menu(wx.Menu):
    def __init__(self, parent, items, *args, **kwargs):
        wx.Menu.__init__(self, *args, **kwargs)
        self.parent = parent
        for data in items:
            if data[0] == SEPARATOR:
                self.AppendSeparator()
            elif data[0] == CHECK:
                # (TYPE, title, ID, callback, activated)
                item = self.AppendCheckItem(data[2], data[1])
                self.Check(data[2], data[4])
                self.parent.Bind(wx.EVT_MENU, data[3], item)
            else:
                # (TYPE, title, ID, callback)
                item = self.Append(data[2], data[1])
                self.parent.Bind(wx.EVT_MENU, data[3], item)


class MenuBar(wx.MenuBar):
    def __init__(self, parent, menus, *args, **kwargs):
        wx.MenuBar.__init__(self, *args, **kwargs)
        self.parent = parent
        for title, items in menus:
            self.Append(Menu(self.parent, items), title)

def SaveBeforeClosing(e):
    if not runtime.project.changed:
        return wx.ID_NO
    result = message(message='If you don''t save, changes will be lost.',
                    title='Save changes before closing?',
                    aStyle=wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL).returned
    if result == wx.ID_YES:
        OnSave(e)
    return result

def OnNew(e):
    if SaveBeforeClosing(e) == wx.ID_CANCEL:
        return
    IO.new()

def OnOpen(e):
    if SaveBeforeClosing(e) == wx.ID_CANCEL:
        return
    path = dialogs.open("Please Choose File",
                        "Scratch 1.4 project file (*.sb)|*.sb"
                        "|All files (*.*)|*.*")
    if path:
        IO.open(path)

def OnSave(e):
    try:
        IO.save()
    except (ValueError, AttributeError):
        OnSaveAs(e)

def OnSaveAs(e):
    path = dialogs.save("Please Choose File",
                        "Scratch 1.4 project file (*.sb)|*.sb"
                        "|All files (*.*)|*.*")
    if path:
        IO.save_as(path)
        return True

def OnQuit(e):
    wx.GetApp().GetTopWindow().Close()

def default_scratch_path():
    if sys.platform == 'win32':
        if os.path.isfile(r'C:\Program Files\Scratch\Scratch.exe'):
            return r'C:\Program Files\Scratch\Scratch.exe'
        elif os.path.isfile(r'C:\Program Files (x86)\Scratch\Scratch.exe'):
            return r'C:\Program Files (x86)\Scratch\Scratch.exe'
    elif sys.platform == 'linux2':
        if os.path.isfile('/usr/bin/scratch'):
            return '/usr/bin/scratch'
    elif sys.platform == 'darwin':
        if os.path.isfile('/Applications/Scratch 1.4/Scratch.app'):
            return '/Applications/Scratch 1.4/Scratch.app'
    return None

def OnSaveAndOpenInScratch(e):
    OnSave(e)

    #Assuring event was not canceled from save as dialog
    if not runtime.project.path: return

    path = config.setdefault('SCRATCH_PATH', default_scratch_path())
    if not path:
        path = dialogs.open("Please Choose The Scratch Executable")
        if path:
            config['SCRATCH_PATH'] = path
        else:
            return

    if sys.platform == 'win32':
        subprocess.Popen([path, os.path.join(os.path.split(path)[0],
                                             'Scratch.image'),
                          runtime.project.path])
    else:
        subprocess.Popen([path, runtime.project.path])

def OnReload(e):
    if not runtime.project.path: return
    IO.reload()

thread = None

def OnStart(e):
    global thread
    if thread and thread.is_alive():
        runtime.engine.trigger(runtime.engine.GREENFLAG_EVENT)
    else:
        runtime.engine.clear_bindings()
        runtime.project.compile_scripts()
        #thread = Thread(target=runtime.engine.start)
        #thread.start()
        runtime.engine.start()

def OnStop(e):
    runtime.engine.stop()

def OnShowStage(event):
    runtime.rightPanel.ShowStage(event.IsChecked())

def OnPreferences(event):
    PreferencesDialog(runtime.mainFrame)

def OnAbout(e):
    description = """M30W is a program designed to allow fast
developing of Scratch projects.
It uses a unique text syntax to allow typing of
blocks rather than laggy dragging them around."""
    mlicense = """M30W is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see http://www.gnu.org/licenses/"""
    info = wx.AboutDialogInfo()

    info.SetIcon(media.get_icon('M30W', wx.Icon, '.ico'))
    info.SetName('M30W')
    info.SetVersion('0.2.0')
    info.SetDescription(description)
    info.SetCopyright('(C) 2012 M30W developers')
    info.SetWebSite('http://scratch.mit.edu/forums/viewtopic.php?id=106225')
    info.SetLicence(mlicense)

    wx.AboutBox(info)

def OnConsole(event):
    sys.stdout = ErrorConsole(None)

def OnPrint(event):
    print_not_implemented_functions()


#===============================================================================
# Different kinds of menu items:
# (NORMAL, '&Title\tCtrl+X', ID, callback)
# (SEPARATOR, )
# (CHECK, 'Title\tCtrl+X', ID, callback, activated)
#===============================================================================

File = ((NORMAL, '&New\tCtrl+N', wx.ID_NEW, OnNew),
        (NORMAL, '&Open\tCtrl+O', wx.ID_OPEN, OnOpen),
        (SEPARATOR,),
        (NORMAL, '&Save\tCtrl+S', wx.ID_SAVE, OnSave),
        (NORMAL, 'Save &As\tCtrl+Shift+S', wx.ID_SAVEAS, OnSaveAs),
        (SEPARATOR,),
        (NORMAL, '&Quit', wx.ID_EXIT, OnQuit))
Edit = ((NORMAL, 'Save And Open In Scratch', wx.ID_ANY, OnSaveAndOpenInScratch),
        (NORMAL, 'Reload', wx.ID_ANY, OnReload),
        (SEPARATOR,),
        (NORMAL, 'Start Scripts', wx.ID_ANY, OnStart),
        (NORMAL, 'Stop Scripts', wx.ID_ANY, OnStop),
        (SEPARATOR,),
        (CHECK, 'Show Stage', wx.ID_PAGE_SETUP, OnShowStage, True),
        (SEPARATOR,),
        (NORMAL, "&Preferences", wx.ID_PREFERENCES, OnPreferences))
Help = [(NORMAL, 'Error Console', wx.ID_ANY, OnConsole),
        (NORMAL, 'Print Not Implemented Functions', wx.ID_ANY, OnPrint),
        (SEPARATOR,),
        (NORMAL, 'About M30W', wx.ID_ABOUT, OnAbout)]

menus = (('&File', File), ('&Edit', Edit), ('&Help', Help))
