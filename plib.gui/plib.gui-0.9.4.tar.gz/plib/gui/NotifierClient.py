#!/usr/bin/env python
"""
Module NotifierClient
Sub-Package GUI of Package PLIB
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the NotifierClient class. This is
a mixin class designed to allow an async socket I/O class
to multiplex its event loop with a GUI event loop. Due to
limitations in some GUI toolkits, this functionality is
implemented in two different ways, depending on the toolkit
in use:

- For Qt 3/4 and KDE 3/4, the PSocketNotifier class is present,
  and its functionality is used to allow the GUI event loop to
  respond to socket events. This is the desired approach.

- For GTK and wxWidgets, there is no straightforward way to
  make the GUI event loop "see" socket events; there are possible
  approaches involving threading, but these are complex and prone
  to brittleness. Instead, the kludgy but workable approach is
  taken of making the asnyc socket I/O ``select`` loop the "primary"
  one, and using the GUI application's ``process_events`` method
  to pump its events based on a ``select`` timeout.
"""

import asyncore
import types

from plib.stdlib.builtins import first
from plib.stdlib.decotools import wraps_class

from plib.gui import main as gui

try:
    from plib.io.async import SocketDispatcher
except ImportError:
    # Dummy class that won't be in anybody's mro
    class SocketDispatcher(object):
        pass


derived_classes = {}


class NotifierClientMeta(type):
    # Evil hack to choose the appropriate functionality depending on
    # whether we are mixing in with an asyncore channel or a plib.io one
    
    def __new__(meta, name, bases, attrs):
        # Note that the middle condition is needed because otherwise we will
        # get a NameError when we construct NotifierClient below!
        if bases and (bases[0] is not object) and (bases[0] is NotifierClient):
            # Find the type of I/O channel we're mixing in with
            channel_class = first(
                klass for klass in bases
                if issubclass(klass, (SocketDispatcher, asyncore.dispatcher))
            )
            if channel_class is None:
                raise TypeError("{} is not a valid I/O channel class!".format(cls.__name__))
            elif issubclass(channel_class, SocketDispatcher):
                from ._notifier_io import NotifierClientMixin
            elif issubclass(channel_class, asyncore.dispatcher):
                from ._notifier_asyncore import NotifierClientMixin
                attrs['dispatcher_class'] = channel_class
            else:
                # This should never happen!
                raise RuntimeError("Broken plib.builtins function: first")
            
            # We have to do it this way because there's no way to use a dynamically
            # determined base class list in a class statement; it would be nice if
            # Python allowed class NotifierClient(*bases), but it doesn't :-)
            bases = (NotifierClientMixin,) + bases
            
            if issubclass(type(channel_class), type):
                # New-style classes are easier, we can just do it the
                # straightforward way; the only thing we have to assume
                # is that there is no metaclass conflict (the interpreter
                # should spot it before we even get here if there is, we
                # put an assert here just to make doubly sure)
                assert issubclass(meta, type(channel_class))
            
            else:
                # Old-style classes are harder because NotifierClient is
                # new-style, so we are mixing the two, which means we have
                # to use some extra hacks to make things work
                assert type(channel_class) is types.ClassType
                assert issubclass(meta, type)  # meta must be new-style
                
                # We assume that no other classes in the MRO have
                # non-trivial constructors, or that the class we're
                # mangling has defined an __init__ to handle it
                if '__init__' not in attrs:
                    # If we don't do this, channel_class's constructor will
                    # never get called because object.__init__ will come before
                    # it in the MRO (and will throw a warning because the
                    # signature isn't right)
                    def _init(self, *args, **kwargs):
                        return channel_class.__init__(self, *args, **kwargs)
                    
                    _init.__name__ = '__init__'
                    attrs['__init__'] = _init
            
            newklass = meta(name, bases, attrs)
            assert issubclass(newklass, channel_class)
            return newklass
        
        else:
            # We aren't a first-level mixin, do things normally
            return type.__new__(meta, name, bases, attrs)


app_obj = None

if hasattr(gui, 'PSocketNotifier'):  # Qt 3/4 and KDE 3/4
    
    from plib.gui.defs import *
    
    notify_methods = {
        NOTIFY_READ: ('readable', 'read'),
        NOTIFY_WRITE: ('writable', 'write')
    }
    
    
    class NotifierClient(object):
        """Mixin class to multiplex async socket client with GUI event loop.
        
        This class is intended to be mixed in with an async socket client
        class; for example::
            
            class MyClient(NotifierClient, async.SocketClient):
                pass
        
        For most purposes this class functions as a "drop-in" mixin; no
        method overrides or other customization should be necessary (other
        than the obvious override of ``process_data`` to do something with
        data received from the socket).
        
        Note that the notifier client object must be instantiated
        *before* the application's event loop is started, or no
        socket events will be processed. (Possible places to do that are
        constructors for any client widget classes, or the app itself
        if you are defining your own app class; or in any methods that
        are called from those constructors, such as the ``_create_panels``
        method of a main panel.)
        
        Note also that we override the ``do_loop`` method to yield control
        back to the GUI event loop, and the ``check_done`` method to
        un-yield so the function that called ``do_loop`` (normally the
        ``client_communicate`` method) can return as it normally would.
        This allows user code to be written portably, so that it does not
        even need to know which event loop is actually running.
        """
        
        __metaclass__ = NotifierClientMeta
        
        notifier_class = gui.PSocketNotifier
        notifiers = None
        
        def get_notifier(self, notify_type):
            sfn, nfn = notify_methods[notify_type]
            result = self.notifier_class(self, notify_type,
                                         getattr(self, sfn),
                                         getattr(asyncore, nfn))
            result.auto_enable = False  # we'll do the re-enable ourselves
            return result
        
        def init_notifiers(self):
            if not self.notifiers:
                self.notifiers = [
                    self.get_notifier(t)
                    for t in (NOTIFY_READ, NOTIFY_WRITE)
                ]
            self.check_notifiers()
        
        def check_notifiers(self):
            if self.notifiers:
                for notifier in self.notifiers:
                    notifier.set_enabled(notifier.select_fn())
        
        def del_notifiers(self):
            if self.notifiers:
                del self.notifiers[:]
        
        # FIXME: Currently we use an ugly hack for Qt/KDE 3 to
        # allow do_loop to be called transparently by a
        # NotifierClient, even though the async I/O loop is not
        # in use. For Qt/KDE 4 there is a documented method for
        # yielding back to the GUI event loop, and un-yielding
        # when necessary; this method is implemented in the
        # enter_yield and exit_yield methods of the application
        # object. For Qt/KDE 3, however, the method used is
        # what is done below if the enter_yield and exit_yield
        # methods are not present on the application object;
        # the documentation says about these method calls, "only
        # do this if you really know what you are doing". This
        # is not very comforting. :-) However, the only other
        # method, calling the async loop with the process_events
        # method of the app object as a callback (as is done for
        # Gtk/wxWidgets below), does not perform well with Qt/KDE,
        # particularly when it is done as a "local" event loop
        # inside a handler for the underlying GUI loop. So we
        # are basically stuck with the ugly hack below. No
        # guarantees are made that this will work reliably; you
        # have been warned. :-) That said, it appears to work on
        # the Linux Qt/KDE implementations I have access to. Given
        # that and the fact that Qt 3 is now being obsoleted, I
        # don't intend to expend much more effort on this issue.
        
        def _doyield(self):
            # Start a local instance of the GUI event loop
            # (NOTE: *not* to be called from user code!)
            if hasattr(app_obj, 'enter_yield'):
                app_obj.enter_yield()
            else:
                # XXX Why does this hack only work if the
                # enterLoop call is made directly from here,
                # instead of wrapping it up in the enter_yield
                # method of the app object?
                app_obj.eventLoop().enterLoop()
        
        def _unyield(self):
            # Return from a local instance of the GUI event loop
            # (NOTE: *not* to be called from user code!)
            if hasattr(app_obj, 'exit_yield'):
                app_obj.exit_yield()
            else:
                # XXX Why does this hack only work if the
                # exitLoop call is made directly from here,
                # instead of wrapping it up in the exit_yield
                # method of the app object?
                app_obj.eventLoop().exitLoop()
    
    
    class NotifierApplication(gui.PApplication):
        
        def createMainWidget(self):
            global app_obj
            app_obj = self
            return super(NotifierApplication, self).createMainWidget()


else:  # GTK and wxWidgets
    
    
    class NotifierClient(object):
        """Mixin class to multiplex async socket client with GUI event loop.
        
        This class is intended to be mixed in with an async socket client
        class; for example::
            
            class MyClient(NotifierClient, async.SocketClient):
                pass
        
        For most purposes this class functions as a "drop-in" mixin; no
        method overrides or other customization should be necessary (other
        than the obvious override of ``process_data`` to do something with
        data received from the socket).
        
        Note that the notifier client object must be instantiated
        *before* the application's event loop is started, or no
        socket events will be processed. (Possible places to do that are
        constructors for any client widget classes, or the app itself
        if you are defining your own app class; or in any methods that
        are called from those constructors, such as the ``_create_panels``
        method of a main panel.)
        """
        
        __metaclass__ = NotifierClientMeta
        
        poll_timeout = 0.1  # needs to be a short timeout to keep GUI snappy
        
        def set_app(self):
            if app_obj.notifier_client is None:
                app_obj.notifier_client = self
        
        def clear_app(self):
            if app_obj.notifier_client is self:
                app_obj.notifier_client = None
    
    
    class NotifierApplication(gui.PApplication):
        
        notifier_client = None
        
        def createMainWidget(self):
            global app_obj
            app_obj = self
            return super(NotifierApplication, self).createMainWidget()
        
        def _eventloop(self):
            """Use the async I/O loop with a timeout to process GUI events.
            """
            if self.notifier_client is not None:
                self.process_events()  # start with a clean slate
                self.notifier_client.do_loop(self.process_events)
                self.process_events()  # clear all events before exiting
            else:
                super(NotifierApplication, self)._eventloop()


gui.default_appclass[0] = NotifierApplication
