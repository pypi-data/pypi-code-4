
# Copyright (C) 2013 LiuLang <gsushzhsosgsu@gmail.com>

# Use of this source code is governed by GPLv3 license that can be found
# in http://www.gnu.org/licenses/gpl-3.0.html

import os
import sys

from Xlib import display
from Xlib import X
from Xlib import XK
from Xlib.ext import record
from Xlib.protocol import rq

local_dpy = display.Display()
record_dpy = display.Display()

# Create a recording context; we only want key and mouse events
ctx = record_dpy.record_create_context(
        0,
        [record.AllClients],
        [{
            'core_requests': (0, 0),
            'core_replies': (0, 0),
            'ext_requests': (0, 0, 0, 0),
            'ext_replies': (0, 0, 0, 0),
            'delivered_events': (0, 0),
            'device_events': (X.KeyPress, X.MotionNotify),
            #'device_events': (X.KeyPress, X.KeyRelease),
            'errors': (0, 0),
            'client_started': False,
            'client_died': False,
        }])

def bind(callback):
    # Check if the extension is present
    if not record_dpy.has_extension('RECORD'):
        print('Error: RECORD extension not found!')
        return False
        #sys.exit(1)

    record_dpy.record_enable_context(ctx, callback)

    # Finally free the context
    record_dpy.record_free_context(ctx)
    return True

def unbind():
    local_dpy.record_disable_context(ctx)
    local_dpy.flush()
    return
