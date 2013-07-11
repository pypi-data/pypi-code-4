#!/usr/bin/env python
"""
Module WXAPP -- Python wxWidgets Application Objects
Sub-Package GUI.TOOLKITS.WX of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets GUI application objects.
"""

import wx

from plib.gui.defs import *
from plib.gui._base import app

from ._wxcommon import _PWxCommunicator, _wxicons


class PWxMessageBox(app.PMessageBoxBase):
    """Customized wxWidgets message box.
    """
    
    questionmap = {
        answerYes: wx.ID_YES,
        answerNo: wx.ID_NO,
        answerCancel: wx.ID_CANCEL,
        answerOK: wx.ID_OK
    }
    
    def _messagebox(self, type, caption, text,
                    button1, button2=None, button3=None):
        
        style = _wxicons[type]
        buttons = [button1, button2, button3]
        if (wx.ID_YES in buttons) or (wx.ID_NO in buttons):
            style = style | wx.YES_NO
        if wx.ID_OK in buttons:
            style = style | wx.OK
        if wx.ID_CANCEL in buttons:
            style = style | wx.CANCEL
        dlg = wx.MessageDialog(self._parent, text, caption, style)
        # Hack to fix strange button ordering for Yes/No/Cancel
        #b_cancel = dlg.FindWindowById(wx.ID_CANCEL)
        #b_no = dlg.FindWindowById(wx.ID_NO)
        #print b_cancel, b_no
        #if (b_cancel is not None) and (b_no is not None):
        #    b_yes = dlg.FindWindowById(wx.ID_YES)
        #    if b_yes:
        #        b_no.MoveAfterInTabOrder(b_yes)
        #    b_cancel.MoveAfterInTabOrder(b_no)
        result = dlg.ShowModal()
        dlg.Destroy()
        return result


class PWxFileDialog(app.PFileDialogBase):
    
    def _wxfiledialog(self, msg, path, filter, style):
        if filter == "":
            filter = "*"
        dlg = wx.FileDialog(self._parent, msg, path, "", filter, style)
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            retval = dlg.GetPath()
        else:
            retval = ""
        dlg.Destroy()
        return retval
    
    def openfiledialog(self, path, filter):
        return self._wxfiledialog("Select file to open", path, filter,
                                  wx.FD_OPEN)
    
    def savefiledialog(self, path, filter):
        return self._wxfiledialog("Select file to save", path, filter,
                                  wx.FD_SAVE)


def _wx_icon_from_file(filename):
    # Kludgy but gets the job done on all platforms
    return wx.IconFromBitmap(wx.BitmapFromImage(wx.Image(filename)))


class PWxAboutDialog(app.PAboutDialogBase, wx.AboutDialogInfo):
    
    attrmap = {
        'name': "SetName",
        'version': "SetVersion",
        'copyright': "SetCopyright",
        'license': "SetLicense",
        'description': "SetDescription",
        'developers': "SetDevelopers",
        'website': "SetWebSite",
        'icon': "SetIconFromFile"
    }
    
    def __init__(self, parent):
        wx.AboutDialogInfo.__init__(self)
        app.PAboutDialogBase.__init__(self, parent)
    
    def SetIconFromFile(self, filename):
        self.SetIcon(_wx_icon_from_file(filename))
    
    def display(self):
        wx.AboutBox(self)


class _PWxBaseMixin(_PWxCommunicator, wx.Frame):
    """Mixin class for wxWidgets base windows.
    """
    
    def _setup_events(self):
        # 'automagic' connections
        self.setup_notify(SIGNAL_QUERYCLOSE, self.OnCloseWindow, False)
        self.setup_notify(SIGNAL_SHOWEVENT, self.OnShowEvent, False)
    
    def _get_w(self):
        return self.GetClientSizeTuple()[0]
    w = property(_get_w)
    
    def _show_window(self):
        wx.Frame.Show(self)
    
    def _hide_window(self):
        wx.Frame.Hide(self)
    
    def set_caption(self, caption):
        self.SetTitle(caption)
    
    def sizetoscreen(self, maximized):
        if maximized:
            self.Maximize(maximized)
        else:
            displayrect = wx.Display().GetClientArea()
            self.SetSizeWH(displayrect.GetWidth() - self.sizeoffset,
                           displayrect.GetHeight() - self.sizeoffset)
    
    def sizetoclient(self, clientwidth, clientheight):
        self.SetClientSizeWH(clientwidth, clientheight)
    
    def center(self):
        self.CenterOnScreen()
    
    def show_init(self):
        self.Show(True)
    
    def exit(self):
        self.Close()
    
    def OnShowEvent(self, event):
        # generates custom show/hide events from single wxWidgets show event
        if event.GetShow():
            self.do_notify(SIGNAL_SHOWN)
        else:
            self.do_notify(SIGNAL_HIDDEN)
    
    def OnCloseWindow(self, event):
        # 'automagic' method for SIGNAL_QUERYCLOSE
        if event.CanVeto() and not self._canclose():
            event.Veto()
        else:
            # Send the closing signal
            self.do_notify(SIGNAL_CLOSING)
            # Make sure the signal handlers are done before we destroy
            self.ProcessPendingEvents()
            self.Destroy()


class PWxBaseWindow(_PWxBaseMixin, app.PBaseWindowBase):
    """Customized wxWidgets base window class.
    """
    
    def __init__(self, parent, cls=None):
        _PWxBaseMixin.__init__(self, None)
        app.PBaseWindowBase.__init__(self, parent, cls)
        self._setup_events()
    
    def show_init(self):
        app.PBaseWindowBase.show_init(self)
        _PWxBaseMixin.show_init(self)


class _PWxMainMixin(_PWxBaseMixin):
    """Mixin class for wxWidgets top windows and main windows.
    """
    
    messageboxclass = PWxMessageBox
    filedialogclass = PWxFileDialog
    aboutdialogclass = PWxAboutDialog
    
    def set_iconfile(self, iconfile):
        self.SetIcon(_wx_icon_from_file(iconfile))
    
    def _size_to_settings(self, width, height):
        self.SetSizeWH(width, height)
        self.SetMinSize((width, height))
    
    def _move_to_settings(self, left, top):
        self.SetPosition(wx.Point(left, top))
    
    def _get_current_geometry(self):
        left, top = self.GetPosition()
        width, height = self.GetSizeTuple()
        return left, top, width, height
    
    def choose_directory(self, curdir):
        dlg = wx.DirDialog(self._parent, defaultPath=curdir)
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            retval = dlg.GetPath()
        else:
            retval = ""
        dlg.Destroy()
        return retval


class PWxTopWindow(_PWxMainMixin, app.PTopWindowBase):
    """Customized wxWidgets top window class.
    """
    
    def __init__(self, parent, cls=None):
        _PWxMainMixin.__init__(self, None)
        app.PTopWindowBase.__init__(self, parent, cls)
        self._setup_events()
    
    def show_init(self):
        app.PTopWindowBase.show_init(self)
        _PWxMainMixin.show_init(self)


class PWxApplication(_PWxCommunicator, wx.App, app.PApplicationBase):
    """Customized wxWidgets application class.
    """
    
    def __init__(self, arglist=[], cls=None, use_mainwindow=False):
        app.PApplicationBase.__init__(self, arglist, cls, use_mainwindow)
        wx.App.__init__(self, arglist)
    
    def OnInit(self):
        # wxWidgets wants you to initialize subwidgets here
        
        self.mainwin = self.createMainWidget()
        self.SetTopWindow(self.mainwin)
        
        # required return value
        return True
    
    def OnExit(self):
        # 'automagic' method for SIGNAL_BEFOREQUIT
        self.before_quit()
    
    def _eventloop(self):
        self.MainLoop()
    
    def process_events(self):
        self.ProcessPendingEvents()
        #self.Yield()
        #wx.SafeYield()
