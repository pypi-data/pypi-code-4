#!/usr/bin/env python3
"""
Module notifier_asyncore -- ASYNCORE mixins for Notifier Client
Sub-Package GUI of Package PLIB3
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

import asyncore

from plib.gui import main as gui

if hasattr(gui, 'PSocketNotifier'):  # Qt 3/4 and KDE 3/4
    
    from functools import wraps
    
    mixin_channels = {}
    asyncore_patched = False
    old_loop = None
    
    class NotifierClientMixin(object):
        
        def _patch_asyncore(self):
            global asyncore_patched
            global old_loop
            
            if not asyncore_patched:
                old_loop = asyncore.loop
                
                @wraps(asyncore.loop)
                def new_loop(*args, **kwargs):
                    # Note that we ignore the normal asyncore.loop args; in
                    # particular there is no way to support a timeout on the
                    # loop--this is not considered a major issue since the
                    # whole point is to keep the GUI snappy while handling
                    # socket events; non-GUI and non-socket operations should
                    # be done in separate threads or processes
                    self._doyield()
                
                asyncore.loop = new_loop
                asyncore_patched = True
            
            mixin_channels[self._fileno] = self
        
        def handle_connect_event(self):
            self.dispatcher_class.handle_connect_event(self)
            if self.connected:
                self._patch_asyncore()
                self.init_notifiers()
        
        def handle_read_event(self):
            self.dispatcher_class.handle_read_event(self)
            if self.connected:
                self.check_notifiers()
        
        def handle_write_event(self):
            self.dispatcher_class.handle_write_event(self)
            if self.connected:
                self.check_notifiers()
        
        def _unpatch_asyncore(self):
            global asyncore_patched
            global old_loop
            
            # Only shut down the GUI event loop if we were the last channel active
            if (not mixin_channels) and asyncore_patched:
                self._unyield()
                asyncore.loop = old_loop
                asyncore_patched = False
                old_loop = None
        
        def close(self):
            self.del_notifiers()
            if self._fileno in mixin_channels:
                # Need to check first since close may be called multiple times
                del mixin_channels[self._fileno]
            self.dispatcher_class.close(self)
            self._unpatch_asyncore()


else:  # GTK and wxWidgets
    
    class NotifierClientMixin(object):
        
        def handle_connect_event(self):
            self.dispatcher_class.handle_connect_event(self)
            if self.connected:
                self.set_app()
        
        def do_loop(self, process_events):
            while asyncore.map:
                asyncore.loop(self.poll_timeout, use_poll=True)
                process_events()
        
        def close(self):
            self.clear_app()
            self.dispatcher_class.close(self)
