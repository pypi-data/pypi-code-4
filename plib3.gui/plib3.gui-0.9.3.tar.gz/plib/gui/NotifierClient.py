#!/usr/bin/env python3
"""
Module NotifierClient
Sub-Package GUI of Package PLIB3
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the NotifierClient class. This is
a mixin class designed to allow an async socket I/O class
to multiplex its event loop with a GUI event loop. Due to
limitations in some GUI toolkits, this functionality is
implemented in two different ways, depending on the toolkit
in use:

- For Qt 4, PySide, and KDE 4, the PSocketNotifier class is present,
  and its functionality is used to allow the GUI event loop to
  respond to socket events. This is the desired approach.

- For wxWidgets, there is no straightforward way to
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

from plib.gui import main as gui

try:
    from plib.io.async import SocketDispatcher
except ImportError:
    # Dummy class that won't be in anybody's mro
    class SocketDispatcher(object):
        pass


app_obj = None

if hasattr(gui, 'PSocketNotifier'):  # Qt 4, PySide, KDE 4
    
    from plib.gui.defs import *
    
    notify_methods = {
        NOTIFY_READ: ('readable', 'read'),
        NOTIFY_WRITE: ('writable', 'write')
    }
    
    
    class NotifierClientBase(object):
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
        
        def _doyield(self):
            # Start a local instance of the GUI event loop
            # (NOTE: *not* to be called from user code!)
            app_obj.enter_yield()
        
        def _unyield(self):
            # Return from a local instance of the GUI event loop
            # (NOTE: *not* to be called from user code!)
            app_obj.exit_yield()
    
    
    class NotifierApplication(gui.PApplication):
        
        def createMainWidget(self):
            global app_obj
            app_obj = self
            return super(NotifierApplication, self).createMainWidget()


else:  # wxWidgets
    
    
    class NotifierClientBase(object):
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


derived_classes = {}


class NotifierClientFactory(object):
    # Evil hack to choose the appropriate functionality depending on
    # whether we are mixing in with an asyncore channel or a plib.io one
    
    def __new__(cls, *args, **kwargs):
        bases = cls.__bases__
        assert bases[0] is NotifierClient
        bases = bases[1:]
        if bases in derived_classes:
            # So we don't do the same class derivation multiple times
            _C = derived_classes[bases]
        
        else:
            # Find the type of I/O channel we're mixing in with
            channel_class = first(
                klass for klass in bases
                if issubclass(klass, (SocketDispatcher, asyncore.dispatcher))
            )
            if channel_class is None:
                raise TypeError("{} is not a valid I/O channel class!".format(cls.__name__))
            elif issubclass(channel_class, SocketDispatcher):
                from ._notifier_io import NotifierClientMixin
                attrs = {}
            elif issubclass(channel_class, asyncore.dispatcher):
                from ._notifier_asyncore import NotifierClientMixin
                attrs = {'dispatcher_class': channel_class}
            else:
                # This should never happen!
                raise RuntimeError("Broken plib.builtins function: first")
            
            # We have to do it this way because there's no way to use a dynamically
            # determined base class list in a class statement; it would be nice if
            # Python allowed class NotifierClient(*bases), but it doesn't :-)
            meta = type(channel_class)
            newbases = (NotifierClientMixin, NotifierClientBase) + bases
            
            attrs.update({
                '__doc__': NotifierClientBase.__doc__
            })
            _C = derived_classes[bases] = meta('NotifierClient', newbases, attrs)
            assert issubclass(_C, channel_class)
        
        # The above removed NotifierClientFactory from the mro, so this
        # will *not* result in an infinite loop back to this method
        return _C(*args, **kwargs)


class NotifierClient(NotifierClientFactory, NotifierClientBase):
    # This is the class that is visible in plib.gui.main; it allows the
    # factory mechanism above to work by slicing NotifierClientFactory out
    # of the mro and replacing it with the appropriate mixin for the type
    # of I/O channel
    pass


gui.default_appclass[0] = NotifierApplication
