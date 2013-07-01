#!/usr/bin/env python3
"""
Module notifier_io -- PLIB3.IO mixins for Notifier Client
Sub-Package GUI of Package PLIB3
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from plib.gui import main as gui

if hasattr(gui, 'PSocketNotifier'):  # Qt 3/4 and KDE 3/4
    
    class NotifierClientMixin(object):
        
        done_callback = None
        yielded = False
        
        def do_connect(self, addr):
            super(NotifierClientMixin, self).do_connect(addr)
            if self.connected or self.connect_pending:
                self.init_notifiers()
        
        def start(self, data):
            super(NotifierClientMixin, self).start(data)
            self.check_notifiers()
        
        def _doyield(self):
            self.yielded = True
            super(NotifierClientMixin, self)._doyield()
        
        def do_loop(self, callback=None):
            """Override to yield back to the GUI event loop.
            """
            self.done_callback = callback
            if not self.yielded:
                self._doyield()
        
        def _unyield(self):
            self.done_callback = None
            self.yielded = False
            super(NotifierClientMixin, self)._unyield()
        
        def handle_write(self):
            super(NotifierClientMixin, self).handle_write()
            self.check_notifiers()
        
        def handle_read(self):
            super(NotifierClientMixin, self).handle_read()
            self.check_notifiers()
        
        def check_done(self):
            """Override to un-yield from the GUI event loop if done.
            """
            super(NotifierClientMixin, self).check_done()
            if self.yielded and (((self.done_callback is not None) and
                                  (self.done_callback() is False)) or
                                 self.done):
                self._unyield()
        
        def close(self):
            """Override to ensure we un-yield when closed.
            """
            super(NotifierClientMixin, self).close()
            if self.yielded:
                self._unyield()
        
        def handle_close(self):
            self.del_notifiers()
            super(NotifierClientMixin, self).handle_close()


else:  # GTK and wxWidgets
    
    class NotifierClientMixin(object):
        
        def do_connect(self, addr):
            super(NotifierClientMixin, self).do_connect(addr)
            if self.connected or self.connect_pending:
                self.set_app()
        
        def handle_close(self):
            self.clear_app()
            super(NotifierClientMixin, self).handle_close()
